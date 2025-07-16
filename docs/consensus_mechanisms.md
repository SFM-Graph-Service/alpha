# Consensus Mechanisms & Governance Design

## Overview
This document outlines the design for implementing consensus mechanisms and automated governance systems to address the identified gap in decision-making automation within the Social Fabric Matrix framework.

## Current State Analysis
- **Gap**: Limited governance and decision-making automation
- **Impact**: Reduces autonomous operation capability and community self-governance
- **Priority**: Medium-High - essential for distributed autonomous organization features

## Governance Framework

### 1. Consensus Types Supported

#### Voting-Based Consensus
- **Simple Majority**: >50% agreement required
- **Supermajority**: Configurable threshold (e.g., 2/3, 3/4)
- **Unanimous**: All participants must agree
- **Weighted Voting**: Vote power based on stakes/reputation

#### Stake-Based Consensus
- **Proof of Stake**: Voting power proportional to resource commitment
- **Delegated Proof of Stake**: Representatives voted by stakeholders
- **Liquid Democracy**: Transitive delegation of voting rights

#### Reputation-Based Consensus
- **Expertise Weighting**: Votes weighted by domain expertise
- **Trust-Based**: Voting power based on trust scores
- **Contribution-Based**: Weight based on historical contributions

## Proposed Implementation

### 1. Consensus Engine

```python
from typing import Dict, List, Optional, Union, Tuple
import uuid
from dataclasses import dataclass, field
from enum import Enum, auto
from datetime import datetime, timedelta
import numpy as np
from core.sfm_models import SFMGraph, Actor, Policy
from core.sfm_enums import RelationshipKind

class ConsensusType(Enum):
    """Types of consensus mechanisms."""
    SIMPLE_MAJORITY = auto()
    SUPERMAJORITY = auto()
    UNANIMOUS = auto()
    WEIGHTED_VOTING = auto()
    PROOF_OF_STAKE = auto()
    DELEGATED_PROOF_OF_STAKE = auto()
    LIQUID_DEMOCRACY = auto()
    REPUTATION_WEIGHTED = auto()

class VoteType(Enum):
    """Types of votes."""
    YES = auto()
    NO = auto()
    ABSTAIN = auto()

class ProposalStatus(Enum):
    """Status of governance proposals."""
    DRAFT = auto()
    VOTING = auto()
    PASSED = auto()
    REJECTED = auto()
    EXPIRED = auto()

@dataclass
class Vote:
    """Individual vote in a proposal."""
    voter_id: uuid.UUID
    vote_type: VoteType
    weight: float = 1.0
    rationale: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    delegated_from: Optional[uuid.UUID] = None

@dataclass
class Proposal:
    """Governance proposal."""
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    title: str = ""
    description: str = ""
    proposer_id: uuid.UUID = field(default_factory=uuid.uuid4)
    proposal_type: str = "general"
    
    # Voting configuration
    consensus_type: ConsensusType = ConsensusType.SIMPLE_MAJORITY
    voting_threshold: float = 0.5
    minimum_participation: float = 0.1
    
    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    voting_starts: datetime = field(default_factory=datetime.now)
    voting_ends: datetime = field(default_factory=lambda: datetime.now() + timedelta(days=7))
    
    # Status and results
    status: ProposalStatus = ProposalStatus.DRAFT
    votes: List[Vote] = field(default_factory=list)
    result: Optional[bool] = None
    participation_rate: float = 0.0
    
    # Metadata
    metadata: Dict[str, any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)

@dataclass
class VoteResult:
    """Result of a voting process."""
    proposal_id: uuid.UUID
    passed: bool
    yes_votes: int
    no_votes: int
    abstain_votes: int
    total_weight_yes: float
    total_weight_no: float
    total_weight_abstain: float
    participation_rate: float
    consensus_achieved: bool
    timestamp: datetime = field(default_factory=datetime.now)

class ConsensusEngine:
    """Implements various consensus mechanisms for governance."""
    
    def __init__(self, graph: SFMGraph):
        self.graph = graph
        self.proposals: Dict[uuid.UUID, Proposal] = {}
        self.delegations: Dict[uuid.UUID, uuid.UUID] = {}  # voter -> delegate
        self.expertise_scores: Dict[uuid.UUID, Dict[str, float]] = {}
        
    def create_proposal(self, title: str, description: str, proposer_id: uuid.UUID,
                       consensus_type: ConsensusType = ConsensusType.SIMPLE_MAJORITY,
                       voting_threshold: float = 0.5,
                       voting_duration: timedelta = timedelta(days=7)) -> uuid.UUID:
        """Create a new governance proposal."""
        
        proposal = Proposal(
            title=title,
            description=description,
            proposer_id=proposer_id,
            consensus_type=consensus_type,
            voting_threshold=voting_threshold,
            voting_ends=datetime.now() + voting_duration
        )
        
        self.proposals[proposal.id] = proposal
        return proposal.id
        
    def cast_vote(self, proposal_id: uuid.UUID, voter_id: uuid.UUID, 
                 vote_type: VoteType, rationale: Optional[str] = None) -> bool:
        """Cast a vote on a proposal."""
        
        if proposal_id not in self.proposals:
            return False
            
        proposal = self.proposals[proposal_id]
        
        # Check if voting is open
        if not self._is_voting_open(proposal):
            return False
            
        # Check if voter is eligible
        if not self._is_voter_eligible(voter_id, proposal):
            return False
            
        # Calculate vote weight
        vote_weight = self._calculate_vote_weight(voter_id, proposal)
        
        # Handle delegation
        delegated_from = self._get_delegation_source(voter_id)
        
        # Create vote
        vote = Vote(
            voter_id=voter_id,
            vote_type=vote_type,
            weight=vote_weight,
            rationale=rationale,
            delegated_from=delegated_from
        )
        
        # Remove any existing vote from this voter
        proposal.votes = [v for v in proposal.votes if v.voter_id != voter_id]
        
        # Add new vote
        proposal.votes.append(vote)
        
        return True
        
    def conduct_weighted_vote(self, proposal_id: uuid.UUID) -> VoteResult:
        """Conduct weighted voting on a proposal."""
        
        if proposal_id not in self.proposals:
            raise ValueError(f"Proposal {proposal_id} not found")
            
        proposal = self.proposals[proposal_id]
        
        # Count votes
        yes_votes = sum(1 for v in proposal.votes if v.vote_type == VoteType.YES)
        no_votes = sum(1 for v in proposal.votes if v.vote_type == VoteType.NO)
        abstain_votes = sum(1 for v in proposal.votes if v.vote_type == VoteType.ABSTAIN)
        
        # Calculate weighted totals
        total_weight_yes = sum(v.weight for v in proposal.votes if v.vote_type == VoteType.YES)
        total_weight_no = sum(v.weight for v in proposal.votes if v.vote_type == VoteType.NO)
        total_weight_abstain = sum(v.weight for v in proposal.votes if v.vote_type == VoteType.ABSTAIN)
        
        total_weight = total_weight_yes + total_weight_no + total_weight_abstain
        
        # Calculate participation rate
        eligible_voters = self._get_eligible_voters(proposal)
        participation_rate = len(proposal.votes) / len(eligible_voters) if eligible_voters else 0
        
        # Determine if consensus achieved
        consensus_achieved = self._check_consensus(proposal, total_weight_yes, total_weight_no, total_weight)
        
        # Determine if proposal passed
        passed = False
        if consensus_achieved and participation_rate >= proposal.minimum_participation:
            if proposal.consensus_type == ConsensusType.SIMPLE_MAJORITY:
                passed = total_weight_yes > total_weight_no
            elif proposal.consensus_type == ConsensusType.SUPERMAJORITY:
                passed = total_weight_yes / total_weight >= proposal.voting_threshold
            elif proposal.consensus_type == ConsensusType.UNANIMOUS:
                passed = total_weight_no == 0 and total_weight_abstain == 0
        
        # Update proposal status
        proposal.status = ProposalStatus.PASSED if passed else ProposalStatus.REJECTED
        proposal.result = passed
        proposal.participation_rate = participation_rate
        
        result = VoteResult(
            proposal_id=proposal_id,
            passed=passed,
            yes_votes=yes_votes,
            no_votes=no_votes,
            abstain_votes=abstain_votes,
            total_weight_yes=total_weight_yes,
            total_weight_no=total_weight_no,
            total_weight_abstain=total_weight_abstain,
            participation_rate=participation_rate,
            consensus_achieved=consensus_achieved
        )
        
        return result
        
    def check_quorum(self, proposal_id: uuid.UUID) -> bool:
        """Check if a proposal has reached quorum."""
        
        if proposal_id not in self.proposals:
            return False
            
        proposal = self.proposals[proposal_id]
        eligible_voters = self._get_eligible_voters(proposal)
        
        participation_rate = len(proposal.votes) / len(eligible_voters) if eligible_voters else 0
        
        return participation_rate >= proposal.minimum_participation
        
    def delegate_vote(self, delegator_id: uuid.UUID, delegate_id: uuid.UUID) -> bool:
        """Delegate voting rights to another actor."""
        
        # Verify both actors exist
        if not self._actor_exists(delegator_id) or not self._actor_exists(delegate_id):
            return False
            
        # Prevent self-delegation
        if delegator_id == delegate_id:
            return False
            
        # Prevent circular delegation
        if self._would_create_circular_delegation(delegator_id, delegate_id):
            return False
            
        self.delegations[delegator_id] = delegate_id
        return True
        
    def revoke_delegation(self, delegator_id: uuid.UUID) -> bool:
        """Revoke a voting delegation."""
        
        if delegator_id in self.delegations:
            del self.delegations[delegator_id]
            return True
        return False
        
    def get_delegation_chain(self, actor_id: uuid.UUID) -> List[uuid.UUID]:
        """Get the delegation chain for an actor."""
        
        chain = [actor_id]
        current = actor_id
        
        while current in self.delegations:
            delegate = self.delegations[current]
            if delegate in chain:  # Circular delegation detected
                break
            chain.append(delegate)
            current = delegate
            
        return chain
        
    def _calculate_vote_weight(self, voter_id: uuid.UUID, proposal: Proposal) -> float:
        """Calculate the weight of a vote based on consensus type."""
        
        if proposal.consensus_type == ConsensusType.SIMPLE_MAJORITY:
            return 1.0
        elif proposal.consensus_type == ConsensusType.WEIGHTED_VOTING:
            return self._get_actor_weight(voter_id)
        elif proposal.consensus_type == ConsensusType.PROOF_OF_STAKE:
            return self._get_actor_stake(voter_id)
        elif proposal.consensus_type == ConsensusType.REPUTATION_WEIGHTED:
            return self._get_actor_reputation(voter_id)
        else:
            return 1.0
            
    def _get_actor_weight(self, actor_id: uuid.UUID) -> float:
        """Get the voting weight of an actor."""
        # Implementation depends on how weight is determined
        # Could be based on resources, contributions, etc.
        return 1.0
        
    def _get_actor_stake(self, actor_id: uuid.UUID) -> float:
        """Get the stake of an actor for proof-of-stake voting."""
        # Calculate stake based on resource commitments
        return 1.0
        
    def _get_actor_reputation(self, actor_id: uuid.UUID) -> float:
        """Get the reputation score of an actor."""
        # Use trust calculator or reputation system
        return 1.0
        
    def _is_voting_open(self, proposal: Proposal) -> bool:
        """Check if voting is currently open for a proposal."""
        now = datetime.now()
        return (proposal.voting_starts <= now <= proposal.voting_ends and 
                proposal.status == ProposalStatus.VOTING)
        
    def _is_voter_eligible(self, voter_id: uuid.UUID, proposal: Proposal) -> bool:
        """Check if an actor is eligible to vote on a proposal."""
        return self._actor_exists(voter_id)
        
    def _get_eligible_voters(self, proposal: Proposal) -> List[uuid.UUID]:
        """Get list of eligible voters for a proposal."""
        return [actor.id for actor in self.graph.actors]
        
    def _check_consensus(self, proposal: Proposal, yes_weight: float, 
                        no_weight: float, total_weight: float) -> bool:
        """Check if consensus has been achieved."""
        
        if total_weight == 0:
            return False
            
        if proposal.consensus_type == ConsensusType.UNANIMOUS:
            return no_weight == 0
        elif proposal.consensus_type == ConsensusType.SUPERMAJORITY:
            return yes_weight / total_weight >= proposal.voting_threshold
        else:
            return True  # Simple majority always has consensus with any votes
            
    def _actor_exists(self, actor_id: uuid.UUID) -> bool:
        """Check if an actor exists in the graph."""
        return any(actor.id == actor_id for actor in self.graph.actors)
        
    def _would_create_circular_delegation(self, delegator_id: uuid.UUID, 
                                        delegate_id: uuid.UUID) -> bool:
        """Check if delegation would create a circular chain."""
        chain = self.get_delegation_chain(delegate_id)
        return delegator_id in chain
        
    def _get_delegation_source(self, voter_id: uuid.UUID) -> Optional[uuid.UUID]:
        """Get the original delegator if this is a delegated vote."""
        for delegator, delegate in self.delegations.items():
            if delegate == voter_id:
                return delegator
        return None
        
    def get_governance_metrics(self) -> Dict[str, any]:
        """Get metrics about the governance system."""
        total_proposals = len(self.proposals)
        passed_proposals = sum(1 for p in self.proposals.values() if p.result is True)
        
        avg_participation = np.mean([p.participation_rate for p in self.proposals.values() 
                                   if p.participation_rate > 0])
        
        return {
            "total_proposals": total_proposals,
            "passed_proposals": passed_proposals,
            "rejection_rate": 1 - (passed_proposals / total_proposals) if total_proposals > 0 else 0,
            "average_participation": avg_participation,
            "active_delegations": len(self.delegations),
            "consensus_types_used": list(set(p.consensus_type for p in self.proposals.values()))
        }
```

### 2. Integration with SFM Service

```python
# In core/sfm_service.py
class SFMService:
    def __init__(self, config: SFMServiceConfig):
        # ... existing initialization
        self.consensus_engine = ConsensusEngine(self.graph)
        
    def create_proposal(self, title: str, description: str, proposer_id: uuid.UUID,
                       consensus_type: ConsensusType = ConsensusType.SIMPLE_MAJORITY) -> uuid.UUID:
        """Create a governance proposal."""
        return self.consensus_engine.create_proposal(title, description, proposer_id, consensus_type)
        
    def cast_vote(self, proposal_id: uuid.UUID, voter_id: uuid.UUID, 
                 vote_type: VoteType, rationale: Optional[str] = None) -> bool:
        """Cast a vote on a proposal."""
        return self.consensus_engine.cast_vote(proposal_id, voter_id, vote_type, rationale)
        
    def conduct_vote(self, proposal_id: uuid.UUID) -> VoteResult:
        """Conduct voting on a proposal."""
        return self.consensus_engine.conduct_weighted_vote(proposal_id)
        
    def delegate_vote(self, delegator_id: uuid.UUID, delegate_id: uuid.UUID) -> bool:
        """Delegate voting rights."""
        return self.consensus_engine.delegate_vote(delegator_id, delegate_id)
        
    def get_governance_metrics(self) -> Dict[str, any]:
        """Get governance system metrics."""
        return self.consensus_engine.get_governance_metrics()
```

### 3. Governance Policy Integration

```python
# Enhanced Policy model for governance
@dataclass
class GovernancePolicy(Policy):
    """Policy specifically for governance rules."""
    
    voting_mechanism: ConsensusType = ConsensusType.SIMPLE_MAJORITY
    voting_threshold: float = 0.5
    minimum_participation: float = 0.1
    voting_duration: timedelta = timedelta(days=7)
    
    # Eligibility criteria
    eligibility_requirements: Dict[str, any] = field(default_factory=dict)
    
    # Implementation details
    automatic_implementation: bool = False
    implementation_delay: timedelta = timedelta(days=0)
```

## Testing Strategy

```python
# tests/test_consensus_engine.py
class TestConsensusEngine(unittest.TestCase):
    
    def test_simple_majority_voting(self):
        """Test simple majority voting mechanism."""
        # Create proposal
        # Cast votes
        # Verify result
        
    def test_weighted_voting(self):
        """Test weighted voting mechanism."""
        # Create proposal with weighted voting
        # Cast votes with different weights
        # Verify correct calculation
        
    def test_delegation_system(self):
        """Test vote delegation functionality."""
        # Set up delegation
        # Cast votes through delegates
        # Verify delegation chain
        
    def test_quorum_requirements(self):
        """Test quorum requirement enforcement."""
        # Create proposal with quorum
        # Cast insufficient votes
        # Verify rejection due to quorum
```

## Implementation Phases

### Phase 1: Basic Voting (4 weeks)
- Implement simple majority and supermajority voting
- Basic proposal creation and voting
- Quorum checking

### Phase 2: Weighted Systems (4 weeks)
- Implement weighted voting mechanisms
- Stake-based and reputation-based voting
- Vote weight calculation

### Phase 3: Delegation System (3 weeks)
- Implement vote delegation
- Delegation chain management
- Liquid democracy features

### Phase 4: Integration & Testing (3 weeks)
- Integration with SFM service
- Comprehensive testing
- Performance optimization

This implementation provides a comprehensive governance system that enables democratic decision-making within the Social Fabric Matrix framework while maintaining flexibility for different governance models.