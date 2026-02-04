"""
Anomaly Detection Service

Provides automated detection of anomalous form responses:
- Spam detection
- Statistical outlier detection
- Impossible value detection
- Duplicate detection
- Dynamic threshold calculation

Task: T-M2-04 - Predictive Anomaly Detection
Task: M2-EXT-04b - Add auto-thresholding for anomaly detection
"""

import re
import math
import uuid
import json
from typing import Dict, List, Any, Optional
from collections import defaultdict
from datetime import datetime
from flask import current_app

from app.models.Form import FormResponse, AnomalyThreshold, AnomalyBatchScan


class AnomalyDetectionService:
    """Service for detecting anomalous form responses."""
    
    # Spam detection keywords
    SPAM_KEYWORDS = [
        "buy now", "click here", "free money", "winner", "congratulations",
        "limited time", "act now", "call now", "make money", "work from home",
        "earn cash", "no cost", "guaranteed", "100% free", "credit card"
    ]
    
    # Sensitivity thresholds
    Z_SCORE_THRESHOLD = 3.0
    FAST_SUBMISSION_THRESHOLD = 2.0  # seconds
    ALL_CAPS_RATIO_THRESHOLD = 0.8
    MIN_TEXT_LENGTH = 5
    MAX_TEXT_LENGTH = 5000
    
    @classmethod
    def detect_spam(cls, response: Dict, baseline: Dict = None) -> Dict[str, Any]:
        """
        Detect spam-like patterns in responses.
        
        Args:
            response: Response dict with 'text', 'submission_time'
            baseline: Baseline statistics (optional)
            
        Returns:
            Dict with 'score', 'indicators', 'is_spam'
        """
        spam_score = 0
        indicators = []
        text = str(response.get('text', ''))
        text_lower = text.lower()
        submission_time = response.get('submission_time', 999)
        
        # Content-based detection
        for keyword in cls.SPAM_KEYWORDS:
            if keyword in text_lower:
                spam_score += 30
                indicators.append({
                    "name": "spam_keyword",
                    "description": f"Contains spam keyword: {keyword}",
                    "weight": 30
                })
        
        # Pattern-based detection
        # All caps check
        if len(text) > 10:
            caps_count = sum(1 for c in text if c.isupper())
            caps_ratio = caps_count / len(text)
            if caps_ratio >= cls.ALL_CAPS_RATIO_THRESHOLD:
                spam_score += 15
                indicators.append({
                    "name": "all_caps",
                    "description": "Text is predominantly uppercase",
                    "weight": 15
                })
        
        # Excessive punctuation
        punct_count = len(re.findall(r'[!?]{2,}', text))
        if punct_count > 0:
            spam_score += 10 * punct_count
            indicators.append({
                "name": "excessive_punctuation",
                "description": "Excessive punctuation marks",
                "weight": 10 * punct_count
            })
        
        # Timing-based detection
        if submission_time < cls.FAST_SUBMISSION_THRESHOLD:
            spam_score += 25
            indicators.append({
                "name": "fast_submission",
                "description": f"Submitted in {submission_time:.1f} seconds (too fast)",
                "weight": 25
            })
        
        # Length check
        if len(text) < cls.MIN_TEXT_LENGTH:
            spam_score += 10
            indicators.append({
                "name": "too_short",
                "description": "Response is too short to be meaningful",
                "weight": 10
            })
        
        # URL detection
        url_pattern = r'https?://\S+|www\.\S+'
        if re.search(url_pattern, text):
            spam_score += 20
            indicators.append({
                "name": "contains_url",
                "description": "Response contains URLs",
                "weight": 20
            })
        
        return {
            "spam_score": min(spam_score, 100),
            "indicators": indicators,
            "is_spam": spam_score >= 50
        }
    
    @classmethod
    def detect_outliers(cls, responses: List[Dict], baseline: Dict = None) -> List[Dict]:
        """
        Detect statistical outliers using Z-score method.
        
        Args:
            responses: List of response dicts
            baseline: Baseline statistics (calculated if not provided)
            
        Returns:
            List of outlier response dicts
        """
        if not responses:
            return []
        
        # Calculate baseline if not provided
        if not baseline:
            baseline = cls._calculate_baseline(responses)
        
        outliers = []
        
        for resp in responses:
            resp_z_scores = {}
            text = str(resp.get('text', ''))
            
            # Response length Z-score
            length = len(text)
            if baseline.get('std_response_length', 0) > 0:
                z_length = abs(length - baseline['avg_response_length']) / baseline['std_response_length']
                resp_z_scores['length'] = z_length
            
            # Sentiment Z-score (if available)
            sentiment_score = resp.get('sentiment', {}).get('score', 0)
            if baseline.get('std_sentiment_score', 0) > 0:
                z_sentiment = abs(sentiment_score - baseline['avg_sentiment_score']) / baseline['std_sentiment_score']
                resp_z_scores['sentiment'] = z_sentiment
            
            # Check if any Z-score exceeds threshold
            max_z = max(resp_z_scores.values()) if resp_z_scores else 0
            
            if max_z >= cls.Z_SCORE_THRESHOLD:
                outliers.append({
                    "response_id": resp.get('id'),
                    "type": "outlier",
                    "z_scores": resp_z_scores,
                    "confidence": min(max_z / 5, 1.0),
                    "details": {
                        "response_length": length,
                        "length_z_score": resp_z_scores.get('length', 0),
                        "sentiment_z_score": resp_z_scores.get('sentiment', 0)
                    }
                })
        
        return outliers
    
    @classmethod
    def _calculate_baseline(cls, responses: List[Dict]) -> Dict[str, Any]:
        """
        Calculate baseline statistics from responses.
        
        Args:
            responses: List of response dicts
            
        Returns:
            Baseline statistics dict
        """
        if not responses:
            return {
                "avg_response_length": 0,
                "std_response_length": 0,
                "avg_sentiment_score": 0,
                "std_sentiment_score": 0
            }
        
        # Calculate response lengths
        lengths = [len(str(r.get('text', ''))) for r in responses]
        avg_length = sum(lengths) / len(lengths)
        std_length = (sum((l - avg_length) ** 2 for l in lengths) / len(lengths)) ** 0.5
        
        # Calculate sentiment scores
        sentiment_scores = [r.get('sentiment', {}).get('score', 0) for r in responses]
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
        std_sentiment = (sum((s - avg_sentiment) ** 2 for s in sentiment_scores) / len(sentiment_scores)) ** 0.5 if sentiment_scores else 0
        
        return {
            "avg_response_length": avg_length,
            "std_response_length": std_length,
            "avg_sentiment_score": avg_sentiment,
            "std_sentiment_score": std_sentiment
        }
    
    @classmethod
    def detect_impossible_values(cls, response: Dict, form_schema: Dict = None) -> List[Dict]:
        """
        Detect logically impossible values based on field constraints.
        
        Args:
            response: Response dict with 'data' field
            form_schema: Form schema with field constraints (optional)
            
        Returns:
            List of impossible value detections
        """
        impossibles = []
        data = response.get('data', {})
        
        if not isinstance(data, dict):
            return impossibles
        
        for field_id, value in data.items():
            # Check numeric constraints (if form_schema provides them)
            if isinstance(value, (int, float)):
                # Future date check would go here
                pass
            
            # Check date fields (simplified)
            if isinstance(value, str):
                # Check for future dates if it looks like a date
                if re.match(r'\d{4}-\d{2}-\d{2}', value):
                    try:
                        date_value = datetime.fromisoformat(value)
                        if date_value > datetime.now():
                            impossibles.append({
                                "field": field_id,
                                "value": value,
                                "reason": "Future date in response"
                            })
                    except ValueError:
                        pass
        
        return impossibles
    
    @classmethod
    def detect_duplicates(cls, response: Dict, existing_responses: List[Dict]) -> bool:
        """
        Check if response is a duplicate of existing responses.
        
        Args:
            response: Current response
            existing_responses: List of existing responses
            
        Returns:
            True if duplicate detected
        """
        text = str(response.get('text', '')).lower().strip()
        
        if len(text) < 10:
            return False
        
        for existing in existing_responses:
            existing_text = str(existing.get('text', '')).lower().strip()
            
            # Exact match
            if text == existing_text:
                return True
            
            # High similarity (simplified)
            similarity = cls._calculate_text_similarity(text, existing_text)
            if similarity > 0.9:
                return True
        
        return False
    
    @classmethod
    def _calculate_text_similarity(cls, text1: str, text2: str) -> float:
        """
        Calculate text similarity (Jaccard).
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0-1)
        """
        set1 = set(text1.split())
        set2 = set(text2.split())
        
        if not set1 or not set2:
            return 0.0
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0
    
    @classmethod
    def calculate_dynamic_thresholds(cls, baseline_stats: Dict[str, Any], 
                                    sensitivity: str = "auto") -> Dict[str, Any]:
        """
        Calculate dynamic Z-score thresholds based on data distribution.
        
        Args:
            baseline_stats: Baseline statistics including mean and std dev for each metric
            sensitivity: Detection sensitivity ("auto", "low", "medium", "high")
            
        Returns:
            Threshold configuration dict with Z-score thresholds for different sigma levels
        """
        # Get standard deviations from baseline
        std_length = baseline_stats.get('std_response_length', 0)
        std_sentiment = baseline_stats.get('std_sentiment_score', 0)
        
        # Calculate thresholds based on sensitivity
        if sensitivity == "low":
            # Low sensitivity = higher thresholds (4σ)
            z_score_threshold = 4.0
        elif sensitivity == "high":
            # High sensitivity = lower thresholds (2σ)
            z_score_threshold = 2.0
        elif sensitivity == "medium":
            # Medium sensitivity = standard thresholds (3σ)
            z_score_threshold = 3.0
        else:  # auto
            # Auto: Use adaptive threshold based on data distribution
            # If standard deviation is very low, use higher threshold to avoid false positives
            # If standard deviation is high, use lower threshold to catch more outliers
            avg_std = (std_length + std_sentiment) / 2 if std_length > 0 and std_sentiment > 0 else 1.0
            if avg_std < 0.5:
                z_score_threshold = 4.0  # Low variance = higher threshold
            elif avg_std < 1.5:
                z_score_threshold = 3.0  # Normal variance = standard threshold
            else:
                z_score_threshold = 2.5  # High variance = lower threshold
        
        # Calculate thresholds for different sigma levels
        thresholds = {
            "z_score_threshold": z_score_threshold,
            "z_score_2sigma": 2.0,
            "z_score_3sigma": 3.0,
            "z_score_4sigma": 4.0,
            "active_threshold": z_score_threshold,
            "sensitivity": sensitivity,
            "calculated_at": datetime.now().isoformat()
        }
        
        # Add metric-specific thresholds if std dev is available
        if std_length > 0:
            thresholds["length_thresholds"] = {
                "mean": baseline_stats.get('avg_response_length', 0),
                "std": std_length,
                "lower_2sigma": baseline_stats.get('avg_response_length', 0) - 2 * std_length,
                "upper_2sigma": baseline_stats.get('avg_response_length', 0) + 2 * std_length,
                "lower_3sigma": baseline_stats.get('avg_response_length', 0) - 3 * std_length,
                "upper_3sigma": baseline_stats.get('avg_response_length', 0) + 3 * std_length,
                "lower_4sigma": baseline_stats.get('avg_response_length', 0) - 4 * std_length,
                "upper_4sigma": baseline_stats.get('avg_response_length', 0) + 4 * std_length
            }
        
        if std_sentiment > 0:
            thresholds["sentiment_thresholds"] = {
                "mean": baseline_stats.get('avg_sentiment_score', 0),
                "std": std_sentiment,
                "lower_2sigma": baseline_stats.get('avg_sentiment_score', 0) - 2 * std_sentiment,
                "upper_2sigma": baseline_stats.get('avg_sentiment_score', 0) + 2 * std_sentiment,
                "lower_3sigma": baseline_stats.get('avg_sentiment_score', 0) - 3 * std_sentiment,
                "upper_3sigma": baseline_stats.get('avg_sentiment_score', 0) + 3 * std_sentiment,
                "lower_4sigma": baseline_stats.get('avg_sentiment_score', 0) - 4 * std_sentiment,
                "upper_4sigma": baseline_stats.get('avg_sentiment_score', 0) + 4 * std_sentiment
            }
        
        return thresholds
    
    @classmethod
    def update_baseline(cls, form_id: str, created_by: str = "system") -> Dict[str, Any]:
        """
        Scan all responses for a form and update baseline statistics.
        Stores the baseline in database.
        
        Args:
            form_id: The form ID to update baseline for
            created_by: User or system identifier creating this baseline
            
        Returns:
            Updated baseline statistics dict
        """
        # Fetch all non-deleted responses for the form
        responses = FormResponse.objects(form_id=form_id, deleted=False)
        
        # Calculate baseline statistics
        baseline_stats = cls._calculate_baseline_from_db(responses)
        
        # Calculate dynamic thresholds
        thresholds = cls.calculate_dynamic_thresholds(baseline_stats, sensitivity="auto")
        
        # Store threshold record in database
        threshold_record = AnomalyThreshold(
            form_id=form_id,
            thresholds=thresholds,
            sensitivity="auto",
            baseline_stats=baseline_stats,
            created_by=created_by,
            response_count=len(responses),
            is_manual=False
        )
        threshold_record.save()
        
        return {
            "baseline_stats": baseline_stats,
            "thresholds": thresholds,
            "response_count": len(responses),
            "threshold_id": str(threshold_record.id)
        }
    
    @classmethod
    def _calculate_baseline_from_db(cls, responses) -> Dict[str, Any]:
        """
        Calculate baseline statistics from database responses.
        
        Args:
            responses: QuerySet of FormResponse objects
            
        Returns:
            Baseline statistics dict
        """
        if not responses:
            return {
                "avg_response_length": 0,
                "std_response_length": 0,
                "avg_sentiment_score": 0,
                "std_sentiment_score": 0
            }
        
        # Extract data from responses
        lengths = []
        sentiment_scores = []
        
        for resp in responses:
            # Calculate response length
            text = str(resp.data) if resp.data else ""
            lengths.append(len(text))
            
            # Extract sentiment score if available
            if hasattr(resp, 'ai_results') and resp.ai_results:
                sentiment = resp.ai_results.get('sentiment', {})
                sentiment_scores.append(sentiment.get('score', 0))
        
        # Calculate statistics
        avg_length = sum(lengths) / len(lengths) if lengths else 0
        std_length = (sum((l - avg_length) ** 2 for l in lengths) / len(lengths)) ** 0.5 if lengths else 0
        
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
        std_sentiment = (sum((s - avg_sentiment) ** 2 for s in sentiment_scores) / len(sentiment_scores)) ** 0.5 if sentiment_scores else 0
        
        return {
            "avg_response_length": avg_length,
            "std_response_length": std_length,
            "avg_sentiment_score": avg_sentiment,
            "std_sentiment_score": std_sentiment
        }
    
    @classmethod
    def get_threshold_history(cls, form_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Retrieve threshold changes over time for a form.
        Shows evolution of detection sensitivity.
        
        Args:
            form_id: The form ID to get threshold history for
            limit: Maximum number of records to return
            
        Returns:
            List of threshold history records
        """
        threshold_records = AnomalyThreshold.objects(
            form_id=form_id
        ).order_by('-timestamp').limit(limit)
        
        history = []
        for record in threshold_records:
            history.append({
                "threshold_id": str(record.id),
                "form_id": str(record.form_id),
                "timestamp": record.timestamp.isoformat() if record.timestamp else None,
                "created_at": record.created_at.isoformat() if record.created_at else None,
                "thresholds": record.thresholds,
                "sensitivity": record.sensitivity,
                "baseline_stats": record.baseline_stats,
                "response_count": record.response_count,
                "created_by": record.created_by,
                "is_manual": record.is_manual,
                "manual_adjustment_reason": record.manual_adjustment_reason
            })
        
        return history
    
    @classmethod
    def get_latest_threshold(cls, form_id: str, sensitivity: str = None) -> Optional[Dict[str, Any]]:
        """
        Get the latest threshold configuration for a form.
        
        Args:
            form_id: The form ID to get threshold for
            sensitivity: Optional sensitivity filter
            
        Returns:
            Latest threshold configuration or None
        """
        query = AnomalyThreshold.objects(form_id=form_id)
        
        if sensitivity:
            query = query.filter(sensitivity=sensitivity)
        
        latest = query.order_by('-timestamp').first()
        
        if not latest:
            return None
        
        return {
            "threshold_id": str(latest.id),
            "form_id": str(latest.form_id),
            "timestamp": latest.timestamp.isoformat() if latest.timestamp else None,
            "thresholds": latest.thresholds,
            "sensitivity": latest.sensitivity,
            "baseline_stats": latest.baseline_stats,
            "response_count": latest.response_count,
            "created_by": latest.created_by,
            "is_manual": latest.is_manual
        }
    
    @classmethod
    def set_manual_threshold(cls, form_id: str, thresholds: Dict[str, Any], 
                            created_by: str, reason: str = None) -> Dict[str, Any]:
        """
        Manually set a threshold configuration for a form.
        
        Args:
            form_id: The form ID to set threshold for
            thresholds: Custom threshold configuration
            created_by: User setting the threshold
            reason: Reason for manual adjustment
            
        Returns:
            Created threshold record
        """
        # Get current baseline stats from latest auto threshold
        latest_auto = cls.get_latest_threshold(form_id, sensitivity="auto")
        baseline_stats = latest_auto['baseline_stats'] if latest_auto else {}
        
        threshold_record = AnomalyThreshold(
            form_id=form_id,
            thresholds=thresholds,
            sensitivity=thresholds.get('sensitivity', 'manual'),
            baseline_stats=baseline_stats,
            created_by=created_by,
            is_manual=True,
            manual_adjustment_reason=reason
        )
        threshold_record.save()
        
        return {
            "threshold_id": str(threshold_record.id),
            "form_id": form_id,
            "thresholds": thresholds,
            "baseline_stats": baseline_stats,
            "created_at": threshold_record.created_at.isoformat(),
            "created_by": created_by
        }
    
    @classmethod
    def run_full_detection(cls, responses: List[Dict], sensitivity: str = "medium",
                         detection_types: List[str] = None, use_dynamic_thresholds: bool = False,
                         form_id: str = None, custom_thresholds: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Run complete anomaly detection on responses.
        
        Args:
            responses: List of response dicts
            sensitivity: Detection sensitivity (auto, low, medium, high)
            detection_types: Types of detection to run
            use_dynamic_thresholds: Whether to use dynamic thresholds from database
            form_id: Form ID (required for dynamic thresholds)
            custom_thresholds: Custom threshold configuration to use
            
        Returns:
            Detection results dict
        """
        if detection_types is None:
            detection_types = ["spam", "outlier", "impossible_value", "duplicate"]
        
        # Determine which thresholds to use
        thresholds_config = None
        baseline = None
        
        if use_dynamic_thresholds and form_id:
            # Try to get latest threshold from database
            latest_threshold = cls.get_latest_threshold(form_id, sensitivity)
            if latest_threshold:
                thresholds_config = latest_threshold['thresholds']
                baseline = latest_threshold['baseline_stats']
                cls.Z_SCORE_THRESHOLD = thresholds_config.get('active_threshold', 3.0)
            else:
                # No threshold found, calculate baseline from responses
                baseline = cls._calculate_baseline(responses)
                thresholds_config = cls.calculate_dynamic_thresholds(baseline, sensitivity)
                cls.Z_SCORE_THRESHOLD = thresholds_config.get('active_threshold', 3.0)
        elif custom_thresholds:
            # Use custom thresholds provided
            thresholds_config = custom_thresholds
            baseline = cls._calculate_baseline(responses)
            cls.Z_SCORE_THRESHOLD = thresholds_config.get('z_score_threshold', 3.0)
        else:
            # Use legacy fixed thresholds
            z_thresholds = {"low": 4.0, "medium": 3.0, "high": 2.5, "auto": 3.0}
            cls.Z_SCORE_THRESHOLD = z_thresholds.get(sensitivity, 3.0)
            baseline = cls._calculate_baseline(responses)
            thresholds_config = cls.calculate_dynamic_thresholds(baseline, sensitivity)
        
        anomalies = []
        type_counts = defaultdict(int)
        
        for resp in responses:
            resp_id = resp.get('id')
            
            # Spam detection
            if "spam" in detection_types:
                spam_result = cls.detect_spam(resp, baseline)
                if spam_result['is_spam']:
                    anomalies.append({
                        "response_id": resp_id,
                        "overall_score": spam_result['spam_score'],
                        "severity": "high" if spam_result['spam_score'] >= 70 else "medium",
                        "flags": [{
                            "type": "spam",
                            "confidence": spam_result['spam_score'] / 100,
                            "description": "Spam patterns detected",
                            "details": {
                                "indicators": spam_result['indicators']
                            }
                        }]
                    })
                    type_counts["spam"] += 1
            
            # Outlier detection
            if "outlier" in detection_types:
                outliers = cls.detect_outliers([resp], baseline)
                for outlier in outliers:
                    anomalies.append({
                        "response_id": resp_id,
                        "overall_score": int(outlier['confidence'] * 100),
                        "severity": "medium",
                        "flags": [{
                            "type": "outlier",
                            "confidence": outlier['confidence'],
                            "description": "Statistical outlier detected",
                            "details": outlier['details']
                        }]
                    })
                    type_counts["outlier"] += 1
        
        return {
            "total_responses": len(responses),
            "anomalies_detected": len(anomalies),
            "baseline": baseline,
            "anomalies": anomalies,
            "summary_by_type": dict(type_counts),
            "thresholds_used": thresholds_config,
            "use_dynamic_thresholds": use_dynamic_thresholds
        }
    
    @classmethod
    def scan_batch(cls, form_id: str, response_ids: List[str], scan_config: Dict[str, Any],
                   created_by: str = "system", batch_id: str = None) -> Dict[str, Any]:
        """
        Scan a batch of form responses for anomalies.
        
        Args:
            form_id: The form ID to scan responses for
            response_ids: List of response IDs to scan (not all responses)
            scan_config: Scan configuration dict with:
                - detection_types: List of detection types
                - sensitivity: Detection sensitivity level
                - use_dynamic_thresholds: Whether to use dynamic thresholds
            created_by: User or system identifier creating this batch scan
            batch_id: Optional batch ID (generated if not provided)
            
        Returns:
            Batch scan results with summary
        """
        # Generate batch ID if not provided
        if not batch_id:
            batch_id = f"batch_{uuid.uuid4().hex[:12]}_{int(datetime.now().timestamp())}"
        
        # Prepare scan configuration
        detection_types = scan_config.get('detection_types', ['spam', 'outlier'])
        sensitivity = scan_config.get('sensitivity', 'medium')
        use_dynamic_thresholds = scan_config.get('use_dynamic_thresholds', False)
        
        # Create batch scan record
        batch_scan = AnomalyBatchScan(
            form_id=form_id,
            batch_id=batch_id,
            response_ids=response_ids,
            scan_config=scan_config,
            status='in_progress',
            total_responses=len(response_ids),
            scanned_count=0,
            results_count=0,
            created_by=created_by,
            started_at=datetime.now()
        )
        batch_scan.save()
        
        try:
            # Fetch responses
            responses = FormResponse.objects(id__in=response_ids, form_id=form_id)
            
            # Prepare response data
            response_data = []
            for resp in responses:
                resp_data = {
                    "id": str(resp.id),
                    "text": str(resp.data),
                    "submitted_at": resp.submitted_at.isoformat() if resp.submitted_at else None,
                    "sentiment": resp.ai_results.get('sentiment', {}) if hasattr(resp, 'ai_results') and resp.ai_results else {}
                }
                response_data.append(resp_data)
            
            # Run detection
            results = cls.run_full_detection(
                response_data,
                sensitivity=sensitivity,
                detection_types=detection_types,
                use_dynamic_thresholds=use_dynamic_thresholds,
                form_id=form_id
            )
            
            # Update batch scan with results
            batch_scan.scanned_count = len(response_data)
            batch_scan.results_count = results['anomalies_detected']
            batch_scan.results = results
            batch_scan.summary = {
                "total_responses": results['total_responses'],
                "anomalies_detected": results['anomalies_detected'],
                "summary_by_type": results['summary_by_type']
            }
            batch_scan.status = 'completed'
            batch_scan.completed_at = datetime.now()
            batch_scan.save()
            
            return {
                "batch_id": batch_id,
                "status": "completed",
                "form_id": form_id,
                "total_responses": batch_scan.total_responses,
                "scanned_count": batch_scan.scanned_count,
                "anomalies_detected": batch_scan.results_count,
                "summary": batch_scan.summary,
                "results": results,
                "started_at": batch_scan.started_at.isoformat() if batch_scan.started_at else None,
                "completed_at": batch_scan.completed_at.isoformat() if batch_scan.completed_at else None
            }
        
        except Exception as e:
            # Update batch scan with error
            batch_scan.status = 'failed'
            batch_scan.error_message = str(e)
            batch_scan.completed_at = datetime.now()
            batch_scan.save()
            
            return {
                "batch_id": batch_id,
                "status": "failed",
                "form_id": form_id,
                "error": str(e),
                "started_at": batch_scan.started_at.isoformat() if batch_scan.started_at else None,
                "completed_at": batch_scan.completed_at.isoformat() if batch_scan.completed_at else None
            }
    
    @classmethod
    def get_batch_status(cls, batch_id: str, nocache: bool = False) -> Optional[Dict[str, Any]]:
        """
        Get the status of an in-progress or completed batch scan.
        
        Args:
            batch_id: The batch ID to check status for
            nocache: Whether to bypass cache and fetch from database
            
        Returns:
            Batch scan status with progress and estimated completion time
        """
        # Try to get from cache first (if not bypassing cache)
        if not nocache:
            from app.utils.redis_client import redis_client
            cache_key = f"anomaly_batch_status:{batch_id}"
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
        
        # Fetch from database
        try:
            batch_scan = AnomalyBatchScan.objects(batch_id=batch_id).first()
            
            if not batch_scan:
                return None
            
            # Calculate progress percentage
            progress = 0.0
            if batch_scan.total_responses > 0:
                progress = (batch_scan.scanned_count / batch_scan.total_responses) * 100
            
            # Estimate completion time
            estimated_completion = None
            if batch_scan.status == 'in_progress' and batch_scan.started_at:
                elapsed = (datetime.now() - batch_scan.started_at).total_seconds()
                if batch_scan.scanned_count > 0:
                    rate = batch_scan.scanned_count / elapsed
                    remaining = batch_scan.total_responses - batch_scan.scanned_count
                    if rate > 0:
                        estimated_seconds = remaining / rate
                        estimated_completion = (datetime.now() + 
                                              datetime.timedelta(seconds=estimated_seconds)).isoformat()
            
            # Prepare status response
            status_data = {
                "batch_id": batch_scan.batch_id,
                "form_id": str(batch_scan.form_id),
                "status": batch_scan.status,
                "progress": round(progress, 2),
                "total_responses": batch_scan.total_responses,
                "scanned_count": batch_scan.scanned_count,
                "results_count": batch_scan.results_count,
                "estimated_completion": estimated_completion,
                "started_at": batch_scan.started_at.isoformat() if batch_scan.started_at else None,
                "completed_at": batch_scan.completed_at.isoformat() if batch_scan.completed_at else None,
                "error_message": batch_scan.error_message
            }
            
            # Add results if completed
            if batch_scan.status == 'completed' and batch_scan.results:
                status_data['results'] = batch_scan.results
                status_data['summary'] = batch_scan.summary
            
            # Cache the result (TTL: 5 minutes for in-progress, 1 hour for completed)
            if not nocache:
                from app.utils.redis_client import redis_client
                cache_key = f"anomaly_batch_status:{batch_id}"
                ttl = 300 if batch_scan.status == 'in_progress' else 3600
                redis_client.set(cache_key, json.dumps(status_data), ttl=ttl)
            
            return status_data
        
        except Exception as e:
            return {
                "batch_id": batch_id,
                "status": "error",
                "error": str(e)
            }
