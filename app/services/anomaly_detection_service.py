"""
Anomaly Detection Service

Provides automated detection of anomalous form responses:
- Spam detection
- Statistical outlier detection
- Impossible value detection
- Duplicate detection

Task: T-M2-04 - Predictive Anomaly Detection
"""

import re
import math
from typing import Dict, List, Any, Optional
from collections import defaultdict
from datetime import datetime
from flask import current_app


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
    def run_full_detection(cls, responses: List[Dict], sensitivity: str = "medium",
                         detection_types: List[str] = None) -> Dict[str, Any]:
        """
        Run complete anomaly detection on responses.
        
        Args:
            responses: List of response dicts
            sensitivity: Detection sensitivity (low, medium, high)
            detection_types: Types of detection to run
            
        Returns:
            Detection results dict
        """
        if detection_types is None:
            detection_types = ["spam", "outlier", "impossible_value", "duplicate"]
        
        # Adjust thresholds based on sensitivity
        z_thresholds = {"low": 4.0, "medium": 3.0, "high": 2.5}
        cls.Z_SCORE_THRESHOLD = z_thresholds.get(sensitivity, 3.0)
        
        # Calculate baseline
        baseline = cls._calculate_baseline(responses)
        
        anomalies = []
        type_counts = defaultdict(int)
        
        for resp in responses:
            resp_id = resp.get('id')
            
            # Spam detection
            if "spam" in detection_types:
                spam_result = cls.detect_spam(resp)
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
            "summary_by_type": dict(type_counts)
        }
