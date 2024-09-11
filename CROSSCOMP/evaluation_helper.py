import yaml
from typing import List, Dict, Any
from sklearn.metrics import precision_recall_fscore_support

def evaluate_results(predictions: List[Dict[str, Any]], ground_truth_path: str) -> Dict[str, Dict[str, float]]:
    """Evaluate the anonymization results against ground truth annotations."""
    
    def is_overlap(start1, end1, start2, end2):
        """Check if two entities overlap."""
        return max(start1, start2) < min(end1, end2)

    def calculate_metrics(true_labels, pred_labels):
        """Calculate precision, recall, and F1 score."""
        y_true = [1 if label in true_labels else 0 for label in all_labels]
        y_pred = [1 if label in pred_labels else 0 for label in all_labels]
        return precision_recall_fscore_support(y_true, y_pred, average='macro')

    with open(ground_truth_path, 'r') as f:
        ground_truth_data = yaml.safe_load(f)

    ground_truth_texts = {text['text']: text.get('annotations', []) for text in ground_truth_data.get('texts', [])}

    # Initialize dictionaries to collect metrics by entity type
    all_true_labels = set()
    all_pred_labels = set()
    entity_metrics = {}

    for result in predictions:
        original_text = result['original_text']
        predicted_labels = result['labels']
        ground_truth_labels = ground_truth_texts.get(original_text, [])
        
        # Create sets of label positions for comparison
        true_labels = {(label['start'], label['end'], label['label']) for label in ground_truth_labels}
        pred_labels = {(label['start'], label['end'], label['label']) for label in predicted_labels}

        # Identify overlapping predictions
        overlapping_true_labels = set()
        overlapping_pred_labels = set()
        for true_label in true_labels:
            for pred_label in pred_labels:
                if is_overlap(*true_label[:2], *pred_label[:2]):
                    overlapping_true_labels.add(true_label)
                    overlapping_pred_labels.add(pred_label)

        # Collect global metrics
        all_true_labels.update([(start, end) for start, end, _ in true_labels if (start, end) not in overlapping_true_labels])
        all_pred_labels.update([(start, end) for start, end, _ in pred_labels if (start, end) not in overlapping_pred_labels])
        
        # Collect entity-specific metrics
        for label in true_labels:
            start, end, entity_type = label
            if entity_type not in entity_metrics:
                entity_metrics[entity_type] = {'true': [], 'pred': []}
            if (start, end) not in overlapping_true_labels:
                entity_metrics[entity_type]['true'].append((start, end))
        
        for label in pred_labels:
            start, end, entity_type = label
            if entity_type not in entity_metrics:
                entity_metrics[entity_type] = {'true': [], 'pred': []}
            if (start, end) not in overlapping_pred_labels:
                entity_metrics[entity_type]['pred'].append((start, end))

    # Compute global metrics
    all_labels = list(all_true_labels.union(all_pred_labels))
    precision_global, recall_global, f1_global, _ = calculate_metrics(all_true_labels, all_pred_labels)

    # Compute entity-specific metrics
    entity_metrics_result = {}
    for entity_type, labels in entity_metrics.items():
        precision, recall, f1, _ = calculate_metrics(labels['true'], labels['pred'])
        entity_metrics_result[entity_type] = {
            'precision': precision,
            'recall': recall,
            'f1_score': f1
        }

    # Debugging Information
    print("Debug Info for Results and Extracted Data:")
    for result in predictions:
        original_text = result['original_text']
        predicted_labels = result['labels']
        ground_truth_labels = ground_truth_texts.get(original_text, [])
        print(f"Debug Info for Result - Original Text: {original_text}")
        print(f"Predicted Labels: {predicted_labels}")
        print(f"Ground Truth Labels: {ground_truth_labels}")
        true_labels_set = {(label['start'], label['end'], label['label']) for label in ground_truth_labels}
        pred_labels_set = {(label['start'], label['end'], label['label']) for label in predicted_labels}
        print(f"True Labels Set: {true_labels_set}")
        print(f"Predicted Labels Set: {pred_labels_set}")
        print("="*40)

    # Debugging Information for Metrics Calculation
    print("Debug Info for Global Metrics Calculation")
    print(f"All True Labels: {all_true_labels}")
    print(f"All Predicted Labels: {all_pred_labels}")
    print("="*40)

    print("Debug Info for Entity-Specific Metrics Calculation")
    for entity_type, labels in entity_metrics.items():
        print(f"Entity Type: {entity_type}")
        print(f"True Labels: {labels['true']}")
        print(f"Predicted Labels: {labels['pred']}")
        print("="*40)

    return {
        'global': {
            'precision': precision_global,
            'recall': recall_global,
            'f1_score': f1_global
        },
        'by_entity': entity_metrics_result
    }
