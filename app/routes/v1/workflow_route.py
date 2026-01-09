from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.models.Workflow import FormWorkflow, WorkflowAction
from app.models.Form import Form
from app.utils.decorator import require_roles
from app.utils.api_helper import handle_error
import logging
import ast

workflow_bp = Blueprint('workflow', __name__)
logger = logging.getLogger(__name__)

def validate_condition_syntax(condition_str):
    """Basic syntax check for python condition string"""
    if not condition_str:
        return True
    try:
        ast.parse(condition_str, mode='eval')
        return True
    except SyntaxError:
        return False

@workflow_bp.route('/', methods=['POST'])
@require_roles('admin', 'superadmin')
def create_workflow():
    try:
        data = request.get_json()
        current_user_id = get_jwt_identity()
        
        required_fields = ['name', 'trigger_form_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
                
        # Validate Form (Existence Check)
        trigger_form = Form.objects(id=data['trigger_form_id']).first()
        if not trigger_form:
             return jsonify({'error': 'Trigger form not found'}), 404
             
        # Validate Condition Syntax
        condition = data.get('trigger_condition', 'True')
        if not validate_condition_syntax(condition):
            return jsonify({'error': 'Invalid python syntax in trigger_condition'}), 400

        actions = []
        if 'actions' in data:
            for a_data in data['actions']:
                target_form_id = a_data.get('target_form_id')
                # Optional: Validate target form exists
                if target_form_id:
                     if not Form.objects(id=target_form_id).first():
                         # We could warn, or fail. Let's allow but maybe warn in logs.
                         pass
                
                action = WorkflowAction(
                    type=a_data.get('type'),
                    target_form_id=target_form_id,
                    data_mapping=a_data.get('data_mapping', {}),
                    assign_to_user_field=a_data.get('assign_to_user_field')
                )
                actions.append(action)
        
        workflow = FormWorkflow(
            name=data['name'],
            description=data.get('description'),
            trigger_form_id=data['trigger_form_id'],
            trigger_condition=condition,
            actions=actions,
            is_active=data.get('is_active', True),
            created_by=current_user_id
        )
        workflow.save()
        
        return jsonify({'message': 'Workflow created', 'id': str(workflow.id)}), 201

    except Exception as e:
        return handle_error(e, logger)

@workflow_bp.route('/', methods=['GET'])
@require_roles('admin', 'superadmin')
def list_workflows():
    try:
        # Optional filter by trigger form
        trigger_form_id = request.args.get('trigger_form_id')
        
        if trigger_form_id:
            workflows = FormWorkflow.objects(trigger_form_id=trigger_form_id)
        else:
            workflows = FormWorkflow.objects()
            
        # Collect form IDs to fetch titles
        form_ids = set()
        for w in workflows:
            if w.trigger_form_id:
                form_ids.add(w.trigger_form_id)
        
        form_map = {}
        if form_ids:
            # Helper to fetch only titles? Or generic query
            forms = Form.objects(id__in=list(form_ids)).only('id', 'title')
            for f in forms:
                form_map[str(f.id)] = f.title
                
        result = []
        for w in workflows:
            result.append({
                'id': str(w.id),
                'name': w.name,
                'trigger_form_title': form_map.get(w.trigger_form_id, "Unknown Form"),
                'is_active': w.is_active,
                'action_count': len(w.actions)
            })
            
        return jsonify(result), 200
    except Exception as e:
        return handle_error(e, logger)

@workflow_bp.route('/<id>', methods=['GET'])
@require_roles('admin', 'superadmin')
def get_workflow(id):
    try:
        workflow = FormWorkflow.objects(id=id).first()
        if not workflow:
            return jsonify({'error': 'Workflow not found'}), 404
            
        actions_data = []
        for a in workflow.actions:
            actions_data.append({
                'type': a.type,
                'target_form_id': a.target_form_id,
                'data_mapping': a.data_mapping,
                'assign_to_user_field': a.assign_to_user_field
            })
            
        return jsonify({
            'id': str(workflow.id),
            'name': workflow.name,
            'description': workflow.description,
            'trigger_form_id': workflow.trigger_form_id,
            'trigger_condition': workflow.trigger_condition,
            'is_active': workflow.is_active,
            'actions': actions_data
        }), 200
    except Exception as e:
        return handle_error(e, logger)

@workflow_bp.route('/<id>', methods=['PUT'])
@require_roles('admin', 'superadmin')
def update_workflow(id):
    try:
        workflow = FormWorkflow.objects(id=id).first()
        if not workflow:
            return jsonify({'error': 'Workflow not found'}), 404
            
        data = request.get_json()
        
        if 'name' in data: workflow.name = data['name']
        if 'description' in data: workflow.description = data['description']
        if 'is_active' in data: workflow.is_active = data['is_active']
        
        if 'trigger_form_id' in data:
             tf = Form.objects(id=data['trigger_form_id']).first()
             if not tf:
                  return jsonify({'error': 'Trigger form not found'}), 404
             workflow.trigger_form_id = data['trigger_form_id']
        
        if 'trigger_condition' in data:
            if not validate_condition_syntax(data['trigger_condition']):
                 return jsonify({'error': 'Invalid condition syntax'}), 400
            workflow.trigger_condition = data['trigger_condition']
            
        if 'actions' in data:
            new_actions = []
            for a_data in data['actions']:
                target_form_id = a_data.get('target_form_id')
                
                action = WorkflowAction(
                    type=a_data.get('type'),
                    target_form_id=target_form_id,
                    data_mapping=a_data.get('data_mapping', {}),
                    assign_to_user_field=a_data.get('assign_to_user_field')
                )
                new_actions.append(action)
            workflow.actions = new_actions
            
        workflow.save()
        return jsonify({'message': 'Workflow updated'}), 200
    except Exception as e:
        return handle_error(e, logger)

@workflow_bp.route('/<id>', methods=['DELETE'])
@require_roles('admin', 'superadmin')
def delete_workflow(id):
    try:
        workflow = FormWorkflow.objects(id=id).first()
        if not workflow:
            return jsonify({'error': 'Workflow not found'}), 404
            
        workflow.delete()
        return jsonify({'message': 'Workflow deleted'}), 200
    except Exception as e:
        return handle_error(e, logger)
