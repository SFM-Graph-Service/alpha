# Trust Propagation System Design

## Overview
This document outlines the design for implementing trust propagation algorithms in the Social Fabric Matrix framework to address the identified gap in trust calculation and network-based reputation systems.

## Current State Analysis
- **Missing**: No explicit trust calculation or propagation mechanisms
- **Impact**: Creates opportunities for manipulation and reduces network integrity
- **Priority**: High - critical for economic fairness and system integrity

## Proposed Implementation

### 1. Trust Calculator Class

```python
from typing import Dict, List, Optional, Tuple
import uuid
from dataclasses import dataclass
from enum import Enum
import networkx as nx
from core.sfm_models import SFMGraph, Actor, Relationship
from core.sfm_enums import RelationshipKind

class TrustMetric(Enum):
    """Types of trust metrics supported."""
    PAGERANK = "pagerank"
    EIGENVECTOR = "eigenvector"
    BETWEENNESS = "betweenness"
    CLOSENESS = "closeness"
    HYBRID = "hybrid"

@dataclass
class TrustScore:
    """Trust score with metadata."""
    actor_id: uuid.UUID
    score: float
    metric_type: TrustMetric
    last_updated: datetime
    contributing_factors: Dict[str, float]

class TrustCalculator:
    """Calculates and maintains trust scores across the network."""
    
    def __init__(self, graph: SFMGraph, alpha: float = 0.85):
        self.graph = graph
        self.alpha = alpha  # PageRank damping factor
        self.trust_scores: Dict[uuid.UUID, TrustScore] = {}
        self.trust_network: nx.DiGraph = nx.DiGraph()
        
    def calculate_trust_score(self, actor_id: uuid.UUID, 
                            metric: TrustMetric = TrustMetric.PAGERANK) -> float:
        """Calculate trust score for a specific actor."""
        if metric == TrustMetric.PAGERANK:
            return self._calculate_pagerank_trust(actor_id)
        elif metric == TrustMetric.HYBRID:
            return self._calculate_hybrid_trust(actor_id)
        # Add other metrics as needed
        
    def _calculate_pagerank_trust(self, actor_id: uuid.UUID) -> float:
        """Calculate PageRank-based trust score."""
        # Build trust network from relationships
        self._build_trust_network()
        
        # Calculate PageRank scores
        pagerank_scores = nx.pagerank(self.trust_network, alpha=self.alpha)
        
        return pagerank_scores.get(actor_id, 0.0)
        
    def _build_trust_network(self):
        """Build trust network from SFM relationships."""
        self.trust_network.clear()
        
        # Add actors as nodes
        for actor in self.graph.actors:
            self.trust_network.add_node(actor.id)
            
        # Add weighted edges based on relationships
        for relationship in self.graph.relationships:
            if self._is_trust_relationship(relationship):
                weight = self._calculate_relationship_trust_weight(relationship)
                self.trust_network.add_edge(
                    relationship.source_id, 
                    relationship.target_id, 
                    weight=weight
                )
                
    def _is_trust_relationship(self, relationship: Relationship) -> bool:
        """Determine if a relationship contributes to trust."""
        trust_relationships = {
            RelationshipKind.TRUSTS,
            RelationshipKind.ENDORSES,
            RelationshipKind.COLLABORATES,
            RelationshipKind.FUNDS,
            RelationshipKind.EMPLOYS
        }
        return relationship.kind in trust_relationships
        
    def _calculate_relationship_trust_weight(self, relationship: Relationship) -> float:
        """Calculate trust weight for a relationship."""
        base_weight = relationship.weight or 0.5
        certainty = relationship.certainty or 1.0
        
        # Adjust weight based on relationship type
        type_multipliers = {
            RelationshipKind.TRUSTS: 1.0,
            RelationshipKind.ENDORSES: 0.8,
            RelationshipKind.COLLABORATES: 0.6,
            RelationshipKind.FUNDS: 0.4,
            RelationshipKind.EMPLOYS: 0.3
        }
        
        multiplier = type_multipliers.get(relationship.kind, 0.5)
        return base_weight * certainty * multiplier
        
    def update_trust_network(self, transaction_data: Dict):
        """Update trust scores based on new transactions/interactions."""
        # Implement dynamic trust updates
        pass
        
    def detect_trust_anomalies(self) -> List[uuid.UUID]:
        """Detect actors with suspicious trust patterns."""
        anomalies = []
        
        for actor_id, score in self.trust_scores.items():
            if self._is_trust_anomaly(score):
                anomalies.append(actor_id)
                
        return anomalies
        
    def _is_trust_anomaly(self, trust_score: TrustScore) -> bool:
        """Check if trust score indicates potential manipulation."""
        # Implement anomaly detection logic
        return False
```

### 2. Integration with Existing Architecture

```python
# In core/sfm_service.py
class SFMService:
    def __init__(self, config: SFMServiceConfig):
        # ... existing initialization
        self.trust_calculator = TrustCalculator(self.graph)
        
    def get_trust_score(self, actor_id: uuid.UUID) -> float:
        """Get trust score for an actor."""
        return self.trust_calculator.calculate_trust_score(actor_id)
        
    def update_trust_network(self, transaction_data: Dict):
        """Update trust network based on new data."""
        self.trust_calculator.update_trust_network(transaction_data)
        
    def get_trust_anomalies(self) -> List[uuid.UUID]:
        """Get list of actors with suspicious trust patterns."""
        return self.trust_calculator.detect_trust_anomalies()
```

### 3. Enhanced Relationship Types

```python
# Add to core/sfm_enums.py
class RelationshipKind(Enum):
    # ... existing relationships
    
    # Trust-specific relationships
    TRUSTS = auto()
    ENDORSES = auto()
    VOUCHES_FOR = auto()
    RATES_POSITIVELY = auto()
    RATES_NEGATIVELY = auto()
    REPORTS_MISCONDUCT = auto()
    VALIDATES = auto()
    CERTIFIES = auto()
```

## Implementation Plan

### Phase 1: Core Trust Calculation (4 weeks)
- Implement TrustCalculator class with PageRank algorithm
- Add trust-specific relationship types
- Integrate with existing SFMService

### Phase 2: Dynamic Trust Updates (4 weeks)
- Implement transaction-based trust updates
- Add trust decay mechanisms
- Implement trust score persistence

### Phase 3: Advanced Trust Analytics (4 weeks)
- Implement hybrid trust metrics
- Add anomaly detection algorithms
- Implement trust network visualization

### Phase 4: Testing and Validation (2 weeks)
- Comprehensive unit tests
- Integration tests with existing system
- Performance testing with large networks

## Testing Strategy

```python
# tests/test_trust_calculator.py
class TestTrustCalculator(unittest.TestCase):
    
    def test_pagerank_trust_calculation(self):
        """Test PageRank-based trust calculation."""
        # Create test network
        # Calculate trust scores
        # Verify expected rankings
        
    def test_trust_anomaly_detection(self):
        """Test detection of suspicious trust patterns."""
        # Create network with known anomalies
        # Run anomaly detection
        # Verify correct identification
        
    def test_dynamic_trust_updates(self):
        """Test trust score updates based on transactions."""
        # Create initial trust network
        # Process transactions
        # Verify trust score changes
```

## Security Considerations

1. **Sybil Attack Prevention**: Implement identity verification requirements
2. **Trust Manipulation**: Monitor for coordinated trust-boosting attempts
3. **Privacy Protection**: Ensure trust calculations don't leak sensitive information
4. **Audit Trail**: Maintain logs of trust score changes for accountability

## Performance Optimization

1. **Incremental Updates**: Only recalculate affected portions of trust network
2. **Caching**: Cache trust scores with appropriate TTL
3. **Batch Processing**: Process trust updates in batches for efficiency
4. **Distributed Calculation**: Support for distributed trust calculation

## Monitoring and Metrics

1. **Trust Score Distribution**: Monitor overall trust score distribution
2. **Anomaly Rates**: Track frequency of trust anomalies
3. **Calculation Performance**: Monitor trust calculation performance
4. **Network Health**: Track trust network connectivity and structure

This implementation addresses the identified gap in trust propagation while maintaining compatibility with the existing SFM architecture and principles.