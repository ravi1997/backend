from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required, get_jwt
from app.models.Dashboard import Dashboard, DashboardWidget
from app.models.Form import SavedSearch, Form, FormResponse
from app.utils.decorator import require_roles
from app.utils.api_helper import handle_error
import uuid
import logging
from concurrent.futures import ThreadPoolExecutor

dashboard_bp = Blueprint('dashboard', __name__)
logger = logging.getLogger(__name__)

# --- CRUD Operations ---

@dashboard_bp.route('/', methods=['POST'])
@require_roles('admin', 'superadmin')
def create_dashboard():
    """Create a new Dashboard configuration."""
    try:
        data = request.get_json()
        current_user_id = get_jwt_identity()
        
        # Basic Validation
        required_fields = ['title', 'slug']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Check slug uniqueness
        if Dashboard.objects(slug=data['slug']).first():
            return jsonify({'error': 'Slug already exists'}), 409
            
        widgets = []
        if 'widgets' in data:
            for w_data in data['widgets']:
                # Resolve references
                form_ref = None
                saved_search_ref = None
                
                if 'form_id' in w_data:
                    form_ref = Form.objects(id=w_data['form_id']).first()
                if 'saved_search_id' in w_data:
                    saved_search_ref = SavedSearch.objects(id=w_data['saved_search_id']).first()
                    
                widget = DashboardWidget(
                    title=w_data.get('title'),
                    type=w_data.get('type'),
                    form_ref=form_ref,
                    saved_search_ref=saved_search_ref,
                    size=w_data.get('size', 'medium'),
                    refresh_interval=w_data.get('refresh_interval', 300),
                    aggregation_field=w_data.get('aggregation_field'),
                    display_columns=w_data.get('display_columns', []),
                    target_link=w_data.get('target_link'),
                    config=w_data.get('config', {})
                )
                widgets.append(widget)
        
        dashboard = Dashboard(
            title=data['title'],
            slug=data['slug'],
            description=data.get('description'),
            roles=data.get('roles', []),
            layout=data.get('layout', 'grid'),
            widgets=widgets,
            created_by=current_user_id
        )
        dashboard.save()
        
        return jsonify({'message': 'Dashboard created', 'id': str(dashboard.id)}), 201
        
    except Exception as e:
        return handle_error(e, logger)

@dashboard_bp.route('/', methods=['GET'])
@jwt_required()
def list_dashboards():
    """List dashboards accessible to the current user."""
    try:
        jwt_data = get_jwt()
        user_roles = jwt_data.get('roles', [])
        
        # If admin, show all? Or just assigned ones? 
        # SRS: "User must have one of the dashboard's assigned roles"
        # We can implement that strictly. 
        # But creators/admins usually want to see everything they management.
        # For now, let's follow strict RBAC intersection + Admins see all.
        
        if 'superadmin' in user_roles or 'admin' in user_roles:
            dashboards = Dashboard.objects()
        else:
            # MongoEngine 'in' for lists checks if any element matches
            dashboards = Dashboard.objects(roles__in=user_roles)
            
        result = []
        for d in dashboards:
            result.append({
                'id': str(d.id),
                'title': d.title,
                'slug': d.slug,
                'description': d.description,
                'role_count': len(d.roles)
            })
            
        return jsonify(result), 200
        
    except Exception as e:
        return handle_error(e, logger)

@dashboard_bp.route('/<slug>', methods=['GET'])
@jwt_required()
def get_dashboard(slug):
    """
    Get dashboard details AND fetch data for widgets.
    """
    try:
        dashboard = Dashboard.objects(slug=slug).first()
        if not dashboard:
            return jsonify({'error': 'Dashboard not found'}), 404
            
        # Permission check
        jwt_data = get_jwt()
        user_roles = jwt_data.get('roles', [])
        
        has_access = False
        if 'superadmin' in user_roles or 'admin' in user_roles:
            has_access = True
        else:
            if any(role in dashboard.roles for role in user_roles):
                has_access = True
                
        if not has_access:
            return jsonify({'error': 'Forbidden'}), 403
            
        # Fetch Widget Data (Parallel Execution for performance)
        widgets_data = []
        
        # Helper function to resolve search
        def resolve_widget_data(widget):
            res_data = None
            try:
                if widget.type == 'list_view' and widget.saved_search_ref:
                    # Execute Saved Search logic (Simplified for MVP)
                    # We need to construct a query based on saved_search filters
                    search_doc = widget.saved_search_ref
                    
                    # This logic should ideally be shared with response_search endpoint
                    # For now, we return empty list if implementation of complex filter parsing is too big for this file
                    # Or we just return the SavedSearch ID and let frontend fetch it?
                    # MVP: Return the SavedSearch ID and Meta, let frontend do the heavy lifting via search API if needed?
                    # SRS says "Data for all widgets". 
                    # Let's try to fetch simple latest 5 records if form_ref is present
                    if widget.form_ref:
                        form_id = widget.form_ref.id
                        responses = FormResponse.objects(form=form_id, deleted=False).order_by('-submitted_at').limit(5)
                        res_data = [{'id': str(r.id), 'submitted_at': r.submitted_at, 'data': r.data} for r in responses]
                        
                elif widget.type == 'counter':
                    if widget.form_ref:
                        # Simple count
                        count = FormResponse.objects(form=widget.form_ref.id, deleted=False).count()
                        res_data = count
                        
            except Exception as w_err:
                logger.error(f"Widget resolution error: {w_err}")
                res_data = {"error": "Failed to load data"}
                
            return {
                'id': str(widget.id),
                'title': widget.title,
                'type': widget.type,
                'size': widget.size,
                'config': widget.config,
                'data': res_data,
                'layout_props': {'cols': widget.display_columns}
            }

        # Serial execution for safety first, can optimize later if needed
        for w in dashboard.widgets:
            widgets_data.append(resolve_widget_data(w))

        return jsonify({
            'id': str(dashboard.id),
            'title': dashboard.title,
            'layout': dashboard.layout,
            'widgets': widgets_data
        }), 200

    except Exception as e:
        return handle_error(e, logger)

@dashboard_bp.route('/<id>', methods=['PUT'])
@require_roles('admin', 'superadmin')
def update_dashboard(id):
    """Update Dashboard configuration."""
    try:
        dashboard = Dashboard.objects(id=id).first()
        if not dashboard:
            return jsonify({'error': 'Dashboard not found'}), 404
            
        data = request.get_json()
        
        if 'title' in data: dashboard.title = data['title']
        if 'description' in data: dashboard.description = data['description']
        if 'roles' in data: dashboard.roles = data['roles']
        if 'layout' in data: dashboard.layout = data['layout']
        # Widget update logic is complex (replace vs update). 
        # For MVP, full replacement of widgets list is safest if provided.
        if 'widgets' in data:
            new_widgets = []
            for w_data in data['widgets']:
                 # Resolve references again
                form_ref = None
                saved_search_ref = None
                if 'form_id' in w_data:
                    form_ref = Form.objects(id=w_data['form_id']).first()
                if 'saved_search_id' in w_data:
                    saved_search_ref = SavedSearch.objects(id=w_data['saved_search_id']).first()
                    
                widget = DashboardWidget(
                    title=w_data.get('title'),
                    type=w_data.get('type'),
                    form_ref=form_ref,
                    saved_search_ref=saved_search_ref,
                    size=w_data.get('size', 'medium'),
                    refresh_interval=w_data.get('refresh_interval', 300),
                    aggregation_field=w_data.get('aggregation_field'),
                    display_columns=w_data.get('display_columns', []),
                    target_link=w_data.get('target_link'),
                    config=w_data.get('config', {})
                )
                new_widgets.append(widget)
            dashboard.widgets = new_widgets
            
        dashboard.save()
        return jsonify({'message': 'Dashboard updated'}), 200
        
    except Exception as e:
        return handle_error(e, logger)
