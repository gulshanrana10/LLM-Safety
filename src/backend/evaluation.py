from sklearn.metrics import precision_score, recall_score, f1_score
from collections import defaultdict

def calculate_metrics(true_entities, predicted_entities):
    # Debugging: Print the inputs for verification
    print("\n\t\t╭─────────────────────────────────────────────────────────────╮")
    print("\t\t│ Debugging: Inputs for Metric Calculation                  │")
    print("\t\t├─────────────────────────────────────────────────────────────┤")
    print(f"\t\t│ True Entities: {true_entities}                             ")
    print(f"\t\t│ Predicted Entities: {predicted_entities}                   ")
    print("\t\t╰─────────────────────────────────────────────────────────────╯\n")

    # Initialize labels
    true_labels = []
    pred_labels = []

    # Prepare dictionaries to accumulate metrics by entity type
    entity_metrics = defaultdict(lambda: {'true_labels': [], 'pred_labels': []})

    # Flatten lists of entity tuples and their labels
    for true_list, pred_list in zip(true_entities, predicted_entities):
        true_set = set((ent['entity'], ent['start'], ent['end']) for ent in true_list)
        pred_set = set(pred_list)
        
        # Add true and predicted labels
        for ent in true_set:
            entity, start, end = ent
            true_labels.append(1)
            pred_labels.append(1 if (entity, start, end) in pred_set else 0)
        
        for ent in pred_set:
            entity, start, end = ent
            if (entity, start, end) not in true_set:
                true_labels.append(0)
                pred_labels.append(1)

    # Compute global metrics
    global_precision = precision_score(true_labels, pred_labels, average='macro', zero_division=0) * 100
    global_recall = recall_score(true_labels, pred_labels, average='macro', zero_division=0) * 100
    global_f1 = f1_score(true_labels, pred_labels, average='macro', zero_division=0) * 100

    # Compute metrics by entity
    entity_metrics_results = defaultdict(lambda: {'true_labels': [], 'pred_labels': []})
    for true_list, pred_list in zip(true_entities, predicted_entities):
        true_set = set((ent['entity'], ent['start'], ent['end']) for ent in true_list)
        pred_set = set(pred_list)
        
        for ent in true_set:
            entity, start, end = ent
            entity_metrics_results[entity]['true_labels'].append(1)
            entity_metrics_results[entity]['pred_labels'].append(1 if (entity, start, end) in pred_set else 0)
        
        for ent in pred_set:
            entity, start, end = ent
            if (entity, start, end) not in true_set:
                entity_metrics_results[entity]['true_labels'].append(0)
                entity_metrics_results[entity]['pred_labels'].append(1)

    # Compute entity-specific metrics
    entity_metrics_results_final = {}
    for label, metrics in entity_metrics_results.items():
        if metrics['true_labels'] or metrics['pred_labels']:
            precision = precision_score(metrics['true_labels'], metrics['pred_labels'], average='binary', zero_division=0) * 100
            recall = recall_score(metrics['true_labels'], metrics['pred_labels'], average='binary', zero_division=0) * 100
            f1 = f1_score(metrics['true_labels'], metrics['pred_labels'], average='binary', zero_division=0) * 100
        else:
            precision = recall = f1 = 0.0
        entity_metrics_results_final[label] = {
            'precision': precision,
            'recall': recall,
            'f1': f1
        }

    return global_precision, global_recall, global_f1, entity_metrics_results_final
