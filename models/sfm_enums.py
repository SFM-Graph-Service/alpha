"""
Enumerations for the Social Fabric Matrix (SFM) framework.

This module defines controlled vocabularies and classification systems used throughout
the SFM analysis framework, based on F. Gregory Hayden's institutional economics work.
These enumerations provide consistent categorization for values, institutions,
resources, 
flows, and relationships in socio-economic systems.

## Theoretical Foundation

This module implements key concepts from Hayden's Social Fabric Matrix framework:
- **Value Categories**: Multi-dimensional value systems beyond market pricing
- **Institution Layers**: Formal rules, organizations, and informal norms
- **Resource Types**: Comprehensive resource classification for institutional analysis
- **Flow Nature**: Patterns of resource and value movement through systems
- **Relationship Kinds**: Institutional relationships and dependencies

## Usage Patterns

### Basic Usage Examples

```python
# from models import Indicator, Flow, Relationship, Actor, Institution
from models.sfm_enums import ValueCategory, FlowNature, RelationshipKind, ResourceType

# Create an economic indicator
gdp_indicator = Indicator(
    label="GDP Growth",
    value_category=ValueCategory.ECONOMIC,
    measurement_unit="percent",
    current_value=2.5
)

# Create a social indicator with multiple value dimensions  
sustainability_index = Indicator(
    label="Community Sustainability Index",
    value_category=ValueCategory.ENVIRONMENTAL,
    measurement_unit="index_score",
    current_value=75.2
)

# Create flows between actors
financial_flow = Flow(
    label="Subsidy Payment",
    nature=FlowNature.FINANCIAL,
    flow_type=FlowType.FINANCIAL
)

# Create institutional relationships
government = Actor(label="EPA", sector="Government")
farmers = Actor(label="Local Farmers", sector="Agriculture")

governs_rel = Relationship(
    source_id=government.id,
    target_id=farmers.id,
    kind=RelationshipKind.GOVERNS
)
```

### Integration with SFM Models

The enums integrate seamlessly with core SFM model classes:

- **ValueCategory**: Used in `Indicator` and `ValueSystem` for multi-dimensional
  measurement
- **InstitutionLayer**: Used in `Institution` for Hayden's three-layer framework
- **ResourceType**: Used in `Resource` for comprehensive resource classification
- **FlowNature/FlowType**: Used in `Flow` for movement pattern analysis
- **RelationshipKind**: Used in `Relationship` for institutional dependency mapping

### Validation and Constraints

The module includes validation through `EnumValidator` class that ensures:
- Compatible enum combinations (e.g., FlowNature.FINANCIAL with FlowType.FINANCIAL)
- Contextually appropriate usage (e.g., measurable ValueCategory for
  quantitative indicators)
- Cross-enum relationship consistency

### Type Hints and Patterns

All enums support standard typing patterns:

```python
from typing import Optional, List
from models.sfm_enums import ValueCategory, InstitutionLayer

def create_policy_indicator(
    value_cat: ValueCategory,
    institution_layer: Optional[InstitutionLayer] = None
) -> Indicator:
    # Implementation with proper type checking
    pass

# Enum membership testing
if ValueCategory.ECONOMIC in [ValueCategory.ECONOMIC, ValueCategory.SOCIAL]:
    # Handle economic indicators
    pass
```

## References

- Hayden, F.G. (2006). "Policymaking for a Good Society: The Social Fabric Matrix 
  Approach to Policy Analysis and Program Evaluation"
- Hayden, F.G. (1982). "Social Fabric Matrix: From Perspective to Analytical Tool"
- Hayden, F.G. (1983). "An Evolutionary-Institutional Model for Policy Analysis"
- Tool, M.R. (1977). "A Social Value Theory in Neoinstitutional Economics"

See Also:
    core.sfm_models: Core data structures using these enumerations
    docs.enum_validation_guide: Detailed validation and error handling guide
"""

from __future__ import annotations

from enum import Enum, auto
from typing import Dict, List, Set, Tuple,Type, Callable, Any, Union

# Module metadata
__version__ = "1.0.0"
__author__ = "SFM Development Team"
__all__ = [
    # Core enums
    'ValueCategory',
    'InstitutionLayer',
    'ResourceType',
    'FlowNature',
    'FlowType',
    'PolicyInstrumentType',
    'ChangeType',
    'BehaviorPatternType',
    'FeedbackPolarity',
    'FeedbackType',
    'TemporalFunctionType',
    'ValidationRuleType',
    'SystemPropertyType',
    'RelationshipKind',
    'PowerResourceType',
    'ToolSkillTechnologyType',
    'PathDependencyType',
    'InstitutionalChangeType',
    'TechnologyReadinessLevel',
    'LegitimacySource',
   # Exception classes
    'SFMEnumError',
    'IncompatibleEnumError',
    'InvalidEnumOperationError',
    # Validation utilities
    'EnumValidator',
    'validate_enum_operation',
]

# ───────────────────────────────────────────────
# ENUMERATIONS  (shared controlled vocabularies)
# ───────────────────────────────────────────────


class ValueCategory(Enum):
    """
    Categories of value in Hayden's Social Fabric Matrix framework.
    
    Based on F. Gregory Hayden's institutional analysis, these categories represent
    different dimensions of value creation, distribution, and impact within
    socio-economic systems. Hayden's framework extends beyond market-based value
    measurements to include social, environmental, and institutional dimensions
    essential for comprehensive policy analysis.
    
    ## Theoretical Background
    
    Hayden's SFM approach recognizes that economic systems create multiple types of
    value that cannot be adequately captured by market prices alone. This enum
    implements his multi-dimensional value framework, allowing analysts to track
    social benefits, environmental costs, institutional capacity, and other
    non-market values crucial for policy evaluation.
    
    ## Usage Examples
    
    ### Basic Indicator Creation
    ```python
    # Economic indicator (traditional market-based measurement)
    gdp_growth = Indicator(
        label="GDP Growth Rate",
        value_category=ValueCategory.ECONOMIC,
        measurement_unit="percent_annual",
        current_value=2.3
    )
    
    # Social equity indicator  
    income_inequality = Indicator(
        label="Gini Coefficient",
        value_category=ValueCategory.SOCIAL,
        measurement_unit="gini_index",
        current_value=0.45
    )
    
    # Environmental sustainability indicator
    carbon_footprint = Indicator(
        label="Carbon Emissions per Capita", 
        value_category=ValueCategory.ENVIRONMENTAL,
        measurement_unit="tons_co2_per_person",
        current_value=8.2
    )
    ```
    
    ### Multi-Dimensional Value Analysis
    ```python
    # Complex sustainability indicator spanning multiple value categories
    sustainability_index = Indicator(
        label="Community Sustainability Index",
        value_category=ValueCategory.ENVIRONMENTAL,  # Primary dimension
        measurement_unit="composite_score",
        current_value=68.5
    )
    # Note: Secondary categories can be tracked through metadata or 
    # additional indicator relationships
    ```
    
    ### Policy Impact Measurement
    ```python
    # Institutional capacity indicator for policy evaluation
    governance_quality = Indicator(
        label="Government Effectiveness Score",
        value_category=ValueCategory.INSTITUTIONAL,
        measurement_unit="percentile_rank",
        current_value=85.2
    )
    
    # Educational outcome indicator
    literacy_rate = Indicator(
        label="Adult Literacy Rate",
        value_category=ValueCategory.EDUCATIONAL,
        measurement_unit="percentage",
        current_value=99.1
    )
    ```
    
    ## Value Category Guidance
    
    **Core Hayden Categories** (from original SFM framework):
    - ECONOMIC: Market transactions, monetary flows, financial returns
    - SOCIAL: Distributional equity, social cohesion, community well-being  
    - ENVIRONMENTAL: Resource stocks, ecological integrity, sustainability
    - CULTURAL: Norms, beliefs, heritage, knowledge systems
    - INSTITUTIONAL: Governance quality, rule consistency, organizational capacity
    - TECHNOLOGICAL: Knowledge base, production techniques, innovation systems
    
    **Extended Categories** (for comprehensive analysis):
    Use when core categories are insufficient for capturing specific value dimensions
    relevant to your SFM analysis context.
    
    ## Integration with SFM Models
    
    ValueCategory integrates with:
    - `Indicator`: Primary classification for measurement metrics
    - `ValueSystem`: Hierarchical value structure definition
    - `PolicyInstrument`: Target value areas for policy intervention
    - `ChangeProcess`: Value dimensions affected by institutional change
    
    ## References
    
    - Hayden, F.G. (2006). "Policymaking for a Good Society", Chapter 4: Value Theory
    - Hayden, F.G. (1982). "Social Fabric Matrix: From Perspective to Analytical Tool"
    - Tool, M.R. (1977). "A Social Value Theory in Neoinstitutional Economics"
    - Hodgson, G.M. (1988). "Economics and Institutions", Chapter 8: Values and
  Valuation
    """
    # Original categories
    ECONOMIC = auto()  # Market-priced goods, services, financial returns
    SOCIAL = auto()  # Distributional equity, social cohesion, well-being
    ENVIRONMENTAL = auto()  # Resource stocks, ecological integrity
    CULTURAL = auto()  # Norms, beliefs, heritage
    INSTITUTIONAL = auto()  # Governance quality, rule consistency
    TECHNOLOGICAL = auto()  # Knowledge base, production techniques

    # Additional common SFM value categories
    POLITICAL = auto()  # Power distribution, democratic participation, governance
    EDUCATIONAL = auto()  # Learning outcomes, knowledge transfer, skill development
    HEALTH = auto()  # Public health, medical outcomes, wellness indicators
    SECURITY = auto()  # Safety, defense, risk management, stability
    INFRASTRUCTURE = (
        auto()
    )  # Physical systems, utilities, transportation, communication
    LEGAL = auto()  # Legal frameworks, rights, justice, compliance
    ETHICAL = auto()  # Moral considerations, fairness, integrity
    AESTHETIC = auto()  # Beauty, design quality, artistic value
    RECREATIONAL = auto()  # Leisure, entertainment, quality of life
    SPIRITUAL = auto()  # Religious values, meaning, purpose
    DEMOGRAPHIC = auto()  # Population characteristics, migration, age structure
    SPATIAL = auto()  # Geographic distribution, land use, location value
    TEMPORAL = auto()  # Time preferences, sustainability, intergenerational equity
    INFORMATIONAL = auto()  # Data quality, knowledge systems, communication
    PSYCHOLOGICAL = auto()  # Mental health, stress, satisfaction, motivation
    COMMUNITY = auto()  # Social capital, civic engagement, collective action
    RESOURCE = auto()  # Natural resource management, conservation, efficiency
    PERFORMANCE = auto()  # Effectiveness, efficiency, productivity measures
    QUALITY = auto()  # Standards, excellence, reliability
    ACCESSIBILITY = auto()  # Inclusion, barrier removal, universal design
    RESILIENCE = auto()  # Adaptability, recovery capacity, robustness
    INNOVATION = auto()  # Creativity, research, development, change capacity
    EQUITY = auto()  # Fairness, distributive justice, equal opportunity
    TRANSPARENCY = auto()  # Openness, accountability, information access
    PARTICIPATION = auto()  # Stakeholder involvement, democratic engagement
    SUSTAINABILITY = auto()  # Long-term viability, resource preservation
    DIVERSITY = auto()  # Variety, inclusion, representation
    COOPERATION = auto()  # Collaboration, partnership, collective action
    COMPETITIVENESS = auto()  # Market position, comparative advantage
    MOBILITY = auto()  # Movement, transportation, migration
    COMMUNICATION = auto()  # Information flow, dialogue, understanding
    ADAPTATION = auto()  # Flexibility, responsiveness, evolution
    INTEGRATION = auto()  # Coordination, coherence, synergy
    AUTONOMY = auto()  # Independence, self-determination, freedom
    STABILITY = auto()  # Consistency, predictability, equilibrium
    EFFICIENCY = auto()  # Resource optimization, productivity, waste reduction
    EFFECTIVENESS = auto()  # Goal achievement, impact, outcomes
    ACCOUNTABILITY = auto()  # Responsibility, oversight, governance
    LEGITIMACY = auto()  # Acceptance, authority, credibility
    CAPACITY = auto()  # Capability, resources, potential
    CONNECTIVITY = auto()  # Networks, relationships, linkages
    FLEXIBILITY = auto()  # Adaptability, responsiveness, agility
    SCALABILITY = auto()  # Growth potential, expansion capability
    INTEROPERABILITY = auto()  # Compatibility, integration, coordination

    @classmethod
    def get_core_categories(cls) -> Set['ValueCategory']:
        """Return the six core Hayden framework categories."""
        return {cls.ECONOMIC, cls.SOCIAL, cls.ENVIRONMENTAL, 
                cls.CULTURAL, cls.INSTITUTIONAL, cls.TECHNOLOGICAL}
    
    @classmethod
    def get_extended_categories(cls) -> Set['ValueCategory']:
        """Return extended categories beyond core framework."""
        return set(cls) - cls.get_core_categories()

class InstitutionLayer(Enum):
    """
    Hayden's three-layer institutional framework plus extended institutional forms.

    Based on F. Gregory Hayden's analysis of institutional structure, this enum
represents
    the different layers at which institutions operate within socio-economic systems.
    Hayden's framework distinguishes between formal constitutional rules, organizational
    structures, and informal cultural norms, providing a comprehensive taxonomy for
    institutional analysis in SFM applications.
    
    ## Theoretical Foundation
    
    Hayden's institutional layering concept recognizes that social coordination occurs
    through multiple, interconnected institutional levels. This hierarchical structure
    helps analysts understand how formal rules, organizational structures, and cultural
    norms interact to shape economic behavior and social outcomes.
    
    ## Core Institutional Layers (Hayden's Framework)
    
    **FORMAL_RULE**: Constitutional and legal frameworks
    - Examples: Constitutions, statutes, property law, regulatory frameworks
    - Function: Establishes formal constraints and rights
    - SFM Role: Foundation for institutional matrix analysis
    
    **ORGANIZATION**: Structured collective entities  
    - Examples: Firms, government agencies, NGOs, labor unions, cooperatives
    - Function: Implements and operationalizes formal rules
    - SFM Role: Key actors in resource flows and value creation
    
    **INFORMAL_NORM**: Cultural practices and social expectations
    - Examples: Customs, habits, social expectations, professional ethics
    - Function: Guides behavior through social coordination mechanisms
    - SFM Role: Influences how formal institutions actually function
    
    ## Usage Examples
    
    ### Basic Institution Classification
    ```python
    # Formal legal institution
    environmental_law = Institution(
        label="Clean Air Act",
        layer=InstitutionLayer.FORMAL_RULE,
        description="Federal environmental regulation"
    )
    
    # Organizational institution
    epa = Institution(
        label="Environmental Protection Agency", 
        layer=InstitutionLayer.ORGANIZATION,
        description="Federal environmental regulatory agency"
    )
    
    # Informal institutional norm
    recycling_norm = Institution(
        label="Community Recycling Practices",
        layer=InstitutionLayer.INFORMAL_NORM,
        description="Local cultural practices for waste management"
    )
    ```
    
    ### Institutional Relationship Analysis
    ```python
    # Hierarchical institutional relationships
    constitution = Institution(label="US Constitution",
                               layer=InstitutionLayer.FORMAL_RULE)
    congress = Institution(label="US Congress", layer=InstitutionLayer.ORGANIZATION)
    political_norms = Institution(label="Democratic Norms",
                                  layer=InstitutionLayer.INFORMAL_NORM)
    
    # Relationships showing institutional hierarchy
    implements_rel = Relationship(
        source_id=congress.id,
        target_id=constitution.id,
        kind=RelationshipKind.IMPLEMENTS
    )
    
    guided_by_rel = Relationship(
        source_id=congress.id,
        target_id=political_norms.id,
        kind=RelationshipKind.GUIDED_BY
    )
    ```
    
    ### Extended Institutional Forms
    ```python
    # Market mechanism as institutional form
    carbon_market = Institution(
        label="Carbon Credit Trading System",
        layer=InstitutionLayer.MARKET_MECHANISM,
        description="Market-based environmental policy instrument"
    )
    
    # International institutional regime
    paris_accord = Institution(
        label="Paris Climate Agreement",
        layer=InstitutionLayer.INTERNATIONAL_REGIME,
        description="Global climate governance framework"
    )
    
    # Hybrid public-private institution
    public_private_partnership = Institution(
        label="Infrastructure PPP",
        layer=InstitutionLayer.HYBRID_INSTITUTION,
        description="Mixed governance arrangement for infrastructure"
    )
    ```
    
    ## Integration with SFM Analysis
    
    InstitutionLayer enables:
    - **Hierarchical Analysis**: Understanding how different institutional levels
  interact
    - **Change Process Mapping**: Tracking how changes propagate across
  institutional layers
    - **Policy Design**: Identifying appropriate institutional levels for intervention
    - **Governance Assessment**: Evaluating institutional capacity at different layers
    
    ## Extended Categories
    
    Beyond Hayden's core three layers, the enum includes additional institutional forms
    relevant for contemporary SFM analysis:
    
    - **MARKET_MECHANISM**: Price systems, contracts, trading platforms
    - **NETWORK**: Collaborative structures, alliances, partnerships  
    - **INTERNATIONAL_REGIME**: Transnational agreements, global governance
    - **HYBRID_INSTITUTION**: Public-private partnerships, mixed governance forms
    
    ## References
    
    - Hayden, F.G. (2006). "Policymaking for a Good Society", Chapter 3:
  Institutional Structure
    - Hayden, F.G. (1982). "Social Fabric Matrix: From Perspective to Analytical Tool"
    - North, D.C. (1990). "Institutions, Institutional Change and Economic Performance"
    - Ostrom, E. (2005). "Understanding Institutional Diversity"
    """
    # Existing values
    FORMAL_RULE = auto()  # Constitutions, statutes, property law
    ORGANIZATION = auto()  # Firms, ministries, NGOs, unions
    INFORMAL_NORM = auto()  # Customs, habits, social expectations

    # Additional values
    CULTURAL_VALUE = auto()  # Deep cultural beliefs that underpin institutions
    POLICY_INSTRUMENT = auto()  # Specific implementation tools (taxes, subsidies)
    MARKET_MECHANISM = auto()  # Price systems, contracts, trading platforms
    NETWORK = auto()  # Collaborative structures, alliances, partnerships
    TECHNOLOGICAL_STANDARD = auto()  # Technical specifications and protocols
    PROFESSIONAL_PRACTICE = auto()  # Professional codes, methodologies, best practices
    COMMUNITY_GOVERNANCE = auto()  # Local and community-based governance
    INTERNATIONAL_REGIME = auto()  # Transnational agreements, treaties
    HYBRID_INSTITUTION = auto()  # Public-private partnerships, mixed governance
    KNOWLEDGE_SYSTEM = auto()  # Scientific paradigms, research programs
    PLANNING_FRAMEWORK = auto()  # Strategic planning systems
    REGULATORY_REGIME = auto()  # Enforcement and compliance systems
    TRADITIONAL_AUTHORITY = auto()  # Customary and indigenous governance structures
    EMERGENT_INSTITUTION = auto()  # Newly forming institutional arrangements


class ResourceType(Enum):
    """
    Classification of resource types within Social Fabric Matrix analysis.

    Categorizes different forms of resources that flow through socio-economic systems,
    including traditional economic resources and expanded categories relevant
    to
    institutional and technological analysis. This comprehensive taxonomy enables
    detailed tracking of resource flows, dependencies, and transformations in
    SFM models.
    
    ## Theoretical Background
    
    Resource classification in SFM analysis extends beyond traditional economic
    categories to include social, institutional, and informational resources crucial
    for understanding modern socio-economic systems. This approach reflects the
    institutional economics recognition that economic activity depends on diverse
    resource types, many of which are not captured in conventional economic accounting.
    
    ## Core Resource Categories
    
    **Traditional Economic Resources** (Hayden's original framework):
    - NATURAL: Land, water, raw minerals, biological resources
    - PRODUCED: Machinery, infrastructure, manufactured capital goods  
    - HUMAN: Labor, human capital, skills, knowledge embodied in people
    - INFORMATION: Data, R&D findings, patents, codified knowledge
    
    ## Usage Examples
    
    ### Basic Resource Creation
    ```python
    # Natural resource
    farmland = Resource(
        label="Agricultural Land",
        rtype=ResourceType.NATURAL,
        description="Fertile soil suitable for crop production"
    )
    
    # Produced capital resource  
    manufacturing_equipment = Resource(
        label="Factory Equipment",
        rtype=ResourceType.PRODUCED,
        description="Industrial machinery for production"
    )
    
    # Human capital resource
    skilled_workforce = Resource(
        label="Skilled Engineering Team",
        rtype=ResourceType.HUMAN,
        description="Engineers with renewable energy expertise"
    )
    
    # Information resource
    climate_data = Resource(
        label="Climate Research Database",
        rtype=ResourceType.INFORMATION,
        description="Historical weather and climate datasets"
    )
    ```
    
    ### Financial and Economic Resources
    ```python
    # Financial capital
    investment_fund = Resource(
        label="Green Technology Investment Fund",
        rtype=ResourceType.FINANCIAL,
        description="Capital available for renewable energy projects"
    )
    
    # Credit resource
    development_loan = Resource(
        label="Infrastructure Development Loan",
        rtype=ResourceType.CREDIT,
        description="Long-term financing for public infrastructure"
    )
    ```
    
    ### Social and Network Resources  
    ```python
    # Social capital
    community_networks = Resource(
        label="Local Business Networks", 
        rtype=ResourceType.SOCIAL_CAPITAL,
        description="Trust relationships between local enterprises"
    )
    
    # Reputational resource
    brand_credibility = Resource(
        label="Corporate Environmental Reputation",
        rtype=ResourceType.REPUTATIONAL,
        description="Public trust in company's sustainability practices"
    )
    ```
    
    ### Infrastructure and Physical Resources
    ```python
    # Built infrastructure
    transportation_network = Resource(
        label="Regional Transportation System",
        rtype=ResourceType.TRANSPORTATION,
        description="Roads, rail, and public transit infrastructure"
    )
    
    # Utility infrastructure  
    power_grid = Resource(
        label="Electrical Grid System",
        rtype=ResourceType.UTILITY,
        description="Electricity generation and distribution network"
    )
    ```
    
    ## Resource Flow Analysis
    
    Resources in SFM analysis participate in various flow relationships:
    
    ```python
    # Resource transformation flow
    iron_ore = Resource(label="Iron Ore", rtype=ResourceType.MINERAL)
    steel = Resource(label="Steel", rtype=ResourceType.PRODUCED)
    
    transformation_flow = Flow(
        label="Steel Production",
        nature=FlowNature.CONVERSION,
        flow_type=FlowType.MATERIAL
    )
    
    # Relationships showing resource transformation
    input_rel = Relationship(
        source_id=iron_ore.id,
        target_id=transformation_flow.id,
        kind=RelationshipKind.PROVIDES_INPUT
    )
    
    output_rel = Relationship(
        source_id=transformation_flow.id,
        target_id=steel.id, 
        kind=RelationshipKind.PRODUCES
    )
    ```
    
    ## Extended Resource Categories
    
    **Energy Resources**: FOSSIL_FUEL, RENEWABLE, NUCLEAR, BIOENERGY
    - Enable detailed energy system analysis
    
    **Digital Resources**: DIGITAL, COMPUTATIONAL, DATA, NETWORK_INFRASTRUCTURE  
    - Support analysis of digital economy and information systems
    
    **Institutional Resources**: ORGANIZATIONAL, REGULATORY, MANAGERIAL
    - Capture institutional capacity and governance resources
    
    **Temporal Resources**: TEMPORAL, HISTORICAL, FUTURE_OPTION
    - Enable analysis of time-dependent and path-dependent processes
    
    ## Integration with SFM Models
    
    ResourceType integrates with:
    - `Resource`: Primary classification for all resource entities
    - `Flow`: Specification of what type of resource is flowing
    - `Actor`: Understanding resource ownership and control
    - `PolicyInstrument`: Targeting specific resource types for policy intervention
    
    ## References
    
    - Hayden, F.G. (2006). "Policymaking for a Good Society", Chapter 5:
  Resource Systems
    - Commons, J.R. (1924). "Legal Foundations of Capitalism" 
    - Ostrom, E. (1990). "Governing the Commons: The Evolution of Institutions
  for Collective Action"
    - Lin, N. (2001). "Social Capital: A Theory of Social Structure and Action"
    """
    # Existing values
    NATURAL = auto()  # Land, water, raw minerals
    PRODUCED = auto()  # Machinery, infrastructures
    HUMAN = auto()  # Labor, human capital, skills
    INFORMATION = auto()  # Data, R&D findings, patents

    # Financial and Economic Resources
    FINANCIAL = auto()  # Money, securities, investments, financial instruments
    MONETARY = auto()  # Currency, liquid assets, reserves
    CREDIT = auto()  # Loans, debt instruments, financing capabilities
    EQUITY = auto()  # Ownership shares, stock, investment capital

    # Knowledge and Intellectual Resources
    INTELLECTUAL = auto()  # Patents, copyrights, trademarks, intellectual property
    KNOWLEDGE = auto()  # Explicit knowledge, theories, methodologies
    CULTURAL = auto()  # Cultural heritage, traditions, practices, languages
    CREATIVE = auto()  # Artistic, design, and creative works

    # Social and Network Resources
    SOCIAL_CAPITAL = auto()  # Trust networks, relationships, community bonds
    REPUTATIONAL = auto()  # Brand value, goodwill, credibility
    POLITICAL = auto()  # Influence, power, representation
    ACCESS = auto()  # Rights of entry or use, permissions, privileges

    # Infrastructure and Physical Resources
    BUILT = auto()  # Buildings, physical structures, permanent installations
    UTILITY = auto()  # Water systems, energy grids, telecommunications networks
    TRANSPORTATION = auto()  # Mobility infrastructure, vehicles, transit systems
    HOUSING = auto()  # Residential structures and communities

    # Energy Resources
    FOSSIL_FUEL = auto()  # Coal, oil, natural gas
    RENEWABLE = auto()  # Solar, wind, hydro, geothermal
    NUCLEAR = auto()  # Fission and fusion materials and facilities
    BIOENERGY = auto()  # Biomass, biofuels, organic energy sources

    # Natural Resources Subcategories
    LAND = auto()  # Territory, real estate, soil
    WATER = auto()  # Fresh water, marine resources, aquifers
    MINERAL = auto()  # Metals, stones, extractive resources
    BIOLOGICAL = auto()  # Flora, fauna, genetic resources
    ECOSYSTEM_SERVICE = auto()  # Natural processes, climate regulation, pollination

    # Technological Resources
    DIGITAL = auto()  # Software, algorithms, digital assets
    COMPUTATIONAL = auto()  # Computing capacity, processing power
    DATA = auto()  # Organized information, datasets, records
    NETWORK_INFRASTRUCTURE = auto()  # Internet, telecommunications, connectivity

    # Time-based Resources
    TEMPORAL = auto()  # Time availability, scheduling capacity
    HISTORICAL = auto()  # Past events, precedent, legacy resources
    FUTURE_OPTION = auto()  # Rights to future resources or opportunities

    # Capacity and System Resources
    ORGANIZATIONAL = auto()  # Structural capacity, institutional frameworks
    LOGISTICAL = auto()  # Supply chains, distribution capabilities
    REGULATORY = auto()  # Permits, certifications, compliance assets
    MANAGERIAL = auto()  # Coordination capabilities, administration
    RESILIENCE = auto()  # Adaptive capacity, redundancy, backup systems


class FlowNature(Enum):
    """
    Classification of flow types and patterns in Social Fabric Matrix systems.

    Describes the nature, direction, timing, and purpose of flows of resources,
    information, value, and other elements through socio-economic systems.
    Essential for understanding system dynamics and transformation processes
    in Hayden's institutional analysis framework.
    
    ## Theoretical Foundation
    
    Flow analysis in SFM recognizes that socio-economic systems are fundamentally
    characterized by movements of resources, information, and value between actors
    and institutions. Understanding flow patterns is crucial for identifying
    system bottlenecks, dependencies, and transformation opportunities.
    
    ## Core Flow Types
    
    **Basic Flow Directions**:
    - INPUT: Resources or value entering a process or actor
    - OUTPUT: Products, services, or value leaving a process or actor  
    - TRANSFER: Direct exchange between actors without transformation
    
    ## Usage Examples
    
    ### Basic Flow Creation
    ```python
    # Input flow - resources entering production
    raw_materials_flow = Flow(
        label="Raw Material Supply",
        nature=FlowNature.INPUT,
        flow_type=FlowType.MATERIAL
    )
    
    # Output flow - products leaving production
    finished_goods_flow = Flow(
        label="Manufactured Products",
        nature=FlowNature.OUTPUT,
        flow_type=FlowType.MATERIAL
    )
    
    # Transfer flow - direct exchange
    payment_flow = Flow(
        label="Payment for Goods",
        nature=FlowNature.TRANSFER,
        flow_type=FlowType.FINANCIAL
    )
    ```
    
    ### Transformation-Based Flows
    ```python
    # Conversion of one resource type to another
    energy_conversion = Flow(
        label="Solar to Electrical Conversion",
        nature=FlowNature.CONVERSION,
        flow_type=FlowType.ENERGY
    )
    
    # Resource extraction from natural systems
    mining_flow = Flow(
        label="Mineral Extraction",
        nature=FlowNature.EXTRACTION,
        flow_type=FlowType.MATERIAL
    )
    
    # Recycling and circular economy flows
    recycling_flow = Flow(
        label="Waste Paper Recycling",
        nature=FlowNature.RECYCLING,
        flow_type=FlowType.MATERIAL
    )
    ```
    
    ### Medium-Specific Flows
    ```python
    # Financial flows
    investment_flow = Flow(
        label="Venture Capital Investment",
        nature=FlowNature.FINANCIAL,
        flow_type=FlowType.FINANCIAL
    )
    
    # Information flows
    data_sharing = Flow(
        label="Research Data Sharing",
        nature=FlowNature.INFORMATION,
        flow_type=FlowType.INFORMATION
    )
    
    # Social flows
    knowledge_transfer = Flow(
        label="Skills Transfer Program",
        nature=FlowNature.SOCIAL,
        flow_type=FlowType.SOCIAL
    )
    ```
    
    ### Temporal Pattern Flows
    ```python
    # Continuous steady flows
    utility_service = Flow(
        label="Electrical Power Supply",
        nature=FlowNature.CONTINUOUS,
        flow_type=FlowType.ENERGY
    )
    
    # Seasonal or cyclical flows
    agricultural_cycle = Flow(
        label="Seasonal Crop Harvesting",
        nature=FlowNature.SEASONAL,
        flow_type=FlowType.MATERIAL
    )
    
    # Feedback information flows
    performance_feedback = Flow(
        label="Performance Monitoring Data",
        nature=FlowNature.FEEDBACK,
        flow_type=FlowType.INFORMATION
    )
    ```
    
    ## Flow Integration with SFM Models
    
    ### Actor-to-Actor Flows
    ```python
    # Create actors
    manufacturer = Actor(label="Manufacturing Company", sector="Industry")
    supplier = Actor(label="Raw Material Supplier", sector="Industry")
    
    # Create flow between actors
    supply_chain_flow = Flow(
        label="Component Supply",
        nature=FlowNature.TRANSFER,
        flow_type=FlowType.MATERIAL
    )
    
    # Establish flow relationships
    supply_rel = Relationship(
        source_id=supplier.id,
        target_id=manufacturer.id,
        kind=RelationshipKind.SUPPLIES,
        flows=[supply_chain_flow.id]
    )
    ```
    
    ### Complex Flow Networks
    ```python
    # Multi-directional flows in circular economy
    waste_flow = Flow(
        label="Organic Waste Collection",
        nature=FlowNature.WASTE,
        flow_type=FlowType.MATERIAL
    )
    
    compost_flow = Flow(
        label="Compost Production",
        nature=FlowNature.RECYCLING,
        flow_type=FlowType.MATERIAL
    )
    
    nutrient_flow = Flow(
        label="Soil Nutrient Return",
        nature=FlowNature.CIRCULAR,
        flow_type=FlowType.MATERIAL
    )
    ```
    
    ## Flow Pattern Categories
    
    **Transformation Flows**: CONVERSION, EXTRACTION, PROCESSING, RECYCLING
    - Track resource transformation processes
    
    **Directional Flows**: CIRCULAR, CASCADING, RECIPROCAL, DISTRIBUTIVE
    - Analyze flow patterns and system structure
    
    **Purpose Flows**: PROVISIONING, REGULATING, SUPPORTING, INVESTMENT
    - Understand functional roles of different flows
    
    **Governance Flows**: MANDATE, COMPLIANCE, AUTHORIZATION, REPORTING
    - Track institutional control and coordination mechanisms
    
    ## Integration with Flow Validation
    
    FlowNature works with FlowType and validation systems:
    
    ```python
    # Valid combination - automatically validated
    financial_transfer = Flow(
        label="Grant Payment",
        nature=FlowNature.FINANCIAL,  # Financial nature
        flow_type=FlowType.FINANCIAL  # Financial type
    )
    
    # Invalid combination - will raise validation error
    # Flow(nature=FlowNature.FINANCIAL, flow_type=FlowType.MATERIAL)
    ```
    
    ## References
    
    - Hayden, F.G. (2006). "Policymaking for a Good Society", Chapter 6: System Flows
    - Georgescu-Roegen, N. (1971). "The Entropy Law and the Economic Process"
    - Meadows, D.H. (2008). "Thinking in Systems: A Primer"
    - Checkland, P. (1999). "Systems Thinking, Systems Practice"
    """
    # Current basic flow types
    INPUT = auto()  # Resource or value entering a process
    OUTPUT = auto()  # Product, waste, or value leaving a process
    TRANSFER = auto()  # Exchange between actors without transformation

    # Transformation-based flows
    CONVERSION = auto()  # Resources transformed from one form to another
    EXTRACTION = auto()  # Removal of resources from natural systems
    PROCESSING = auto()  # Intermediate transformation steps
    RECYCLING = auto()  # Reprocessing of materials for reuse
    WASTE = auto()  # Unwanted byproducts or residuals
    DEGRADATION = auto()  # Reduction in quality or utility
    RESTORATION = auto()  # Renewal or repair of resources

    # Medium-based flows
    FINANCIAL = auto()  # Money, credit, financial instruments
    MATERIAL = auto()  # Physical goods and substances
    ENERGY = auto()  # Power, heat, electricity flows
    INFORMATION = auto()  # Data, knowledge, signals
    CULTURAL = auto()  # Values, practices, symbols
    SOCIAL = auto()  # Relationships, trust, social capital
    SERVICE = auto()  # Non-physical value delivery
    REGULATORY = auto()  # Control signals, permissions, constraints

    # Directionality flows
    CIRCULAR = auto()  # Returns to origin after processing
    CASCADING = auto()  # Sequential flows through multiple processes
    RECIPROCAL = auto()  # Bidirectional exchanges
    DISTRIBUTIVE = auto()  # One-to-many flows (distribution)
    CUMULATIVE = auto()  # Flows that build up or accumulate over time
    FEEDBACK = auto()  # Information returned to control processes

    # Temporal pattern flows
    CONTINUOUS = auto()  # Steady, uninterrupted flows
    INTERMITTENT = auto()  # Irregular or sporadic flows
    PULSED = auto()  # Regular bursts of flow
    SEASONAL = auto()  # Flows tied to natural or social cycles
    ACCELERATING = auto()  # Flows increasing in rate
    DECELERATING = auto()  # Flows decreasing in rate
    THRESHOLD = auto()  # Flows that occur after conditions are met

    # Purpose-based flows
    PROVISIONING = auto()  # Providing goods or services
    REGULATING = auto()  # Controlling system processes
    SUPPORTING = auto()  # Enabling other flows or processes
    MAINTENANCE = auto()  # Preserving system functions
    GROWTH = auto()  # Expanding system capacity
    INVESTMENT = auto()  # Building future capacity
    CONSUMPTION = auto()  # Using up resources for immediate benefit

    # Boundary-crossing flows
    IMPORT = auto()  # Flows entering from outside the system
    EXPORT = auto()  # Flows leaving the system
    INTERNAL = auto()  # Flows contained within system boundaries
    TRANSBOUNDARY = auto()  # Flows crossing multiple boundaries
    SPILLOVER = auto()  # Unintended flows across boundaries
    LEAKAGE = auto()  # Unintended escape of resources from system

    # Specific economic flows
    TAXATION = auto()  # Mandatory payments to governmental entities
    SUBSIDY = auto()  # Support payments from government to entities
    DIVIDEND = auto()  # Distribution of profits to shareholders
    WAGE = auto()  # Compensation for labor
    RENT = auto()  # Payment for use of property or resources
    INTEREST = auto()  # Payment for use of borrowed capital

    # Governance and institutional flows
    MANDATE = auto()  # Authoritative directives or requirements
    COMPLIANCE = auto()  # Conformity with rules or standards
    AUTHORIZATION = auto()  # Formal permission or approval
    CERTIFICATION = auto()  # Verification of adherence to standards
    REPORTING = auto()  # Required information disclosure


class FlowType(Enum):
    """
    Classification of flow types by medium/content in Social Fabric Matrix systems.

    Defines the fundamental types of flows that can occur between actors, processes,
    and resources in socio-economic systems. This classification complements FlowNature
    by specifying the medium or content type of what flows through the system.
    
    ## Usage with FlowNature
    
    FlowType works in combination with FlowNature to provide complete flow
    specification:
    
    ```python
    # Financial payment flow
    payment = Flow(
        label="Service Payment",
        nature=FlowNature.TRANSFER,     # How it flows (direct transfer)
        flow_type=FlowType.FINANCIAL    # What flows (money/financial instruments)
    )
    
    # Information sharing flow
    data_sharing = Flow(
        label="Research Data Sharing",
        nature=FlowNature.INFORMATION,  # How it flows (information pattern)
        flow_type=FlowType.INFORMATION  # What flows (data/knowledge)
    )
    
    # Material production flow
    manufacturing = Flow(
        label="Product Manufacturing",
        nature=FlowNature.CONVERSION,   # How it flows (transformation)
        flow_type=FlowType.MATERIAL     # What flows (physical goods)
    )
    ```
    
    ## Flow Type Categories
    
    - **MATERIAL**: Physical goods, substances, manufactured products
    - **ENERGY**: Power, heat, electricity, mechanical energy
    - **INFORMATION**: Data, knowledge, signals, communications
    - **FINANCIAL**: Money, credit, financial instruments, investments
    - **SOCIAL**: Relationships, trust, social capital, cultural practices
    
    ## Integration with Validation
    
    FlowType combinations with FlowNature are automatically validated:
    
    ```python
    # Valid combinations
    Flow(nature=FlowNature.FINANCIAL, flow_type=FlowType.FINANCIAL)  # ✓
    Flow(nature=FlowNature.MATERIAL, flow_type=FlowType.MATERIAL)    # ✓
    Flow(nature=FlowNature.ENERGY, flow_type=FlowType.ENERGY)        # ✓
    
    # Invalid combinations (will raise validation error)
    # Flow(nature=FlowNature.FINANCIAL, flow_type=FlowType.MATERIAL)  # ✗
    ```
    """
    MATERIAL = auto()  # Physical goods and substances
    ENERGY = auto()  # Power, heat, electricity flows
    INFORMATION = auto()  # Data, knowledge, signals
    FINANCIAL = auto()  # Money, credit, financial instruments
    SOCIAL = auto()  # Relationships, trust, social capital


class PolicyInstrumentType(Enum):
    """
    Classification of policy instrument types for implementation analysis.

    Categorizes the different mechanisms through which policies can be implemented
    and enforced in socio-economic systems, based on institutional economics and
    public policy analysis frameworks. Essential for understanding how policy goals
    are translated into specific implementation strategies.
    
    ## Theoretical Background
    
    Policy instrument classification recognizes that governments and institutions have
    multiple tools available for achieving policy objectives. The choice of instrument
    affects implementation costs, compliance mechanisms, distributional impacts, and
    political feasibility. This taxonomy enables systematic analysis of policy design
    choices within SFM frameworks.
    
    ## Core Instrument Types
    
    **REGULATORY**: Command-and-control mechanisms using legal authority
    **ECONOMIC**: Market-based mechanisms using financial incentives
    **VOLUNTARY**: Cooperative mechanisms relying on voluntary compliance
    **INFORMATION**: Education and disclosure mechanisms using information provision
    
    ## Usage Examples
    
    ### Regulatory Instruments
    ```python
    # Environmental regulation
    emission_standard = PolicyInstrument(
        label="Vehicle Emission Standards",
        instrument_type=PolicyInstrumentType.REGULATORY,
        target_behavior="Reduce vehicle emissions",
        compliance_mechanism="Mandatory testing and certification"
    )
    
    # Zoning regulation
    zoning_law = PolicyInstrument(
        label="Industrial Zoning Restrictions", 
        instrument_type=PolicyInstrumentType.REGULATORY,
        target_behavior="Control industrial development location",
        compliance_mechanism="Building permit requirements"
    )
    ```
    
    ### Economic Instruments
    ```python
    # Market-based environmental policy
    carbon_tax = PolicyInstrument(
        label="Carbon Tax",
        instrument_type=PolicyInstrumentType.ECONOMIC,
        target_behavior="Reduce greenhouse gas emissions",
        compliance_mechanism="Tax collection system"
    )
    
    # Subsidy program
    renewable_subsidy = PolicyInstrument(
        label="Solar Panel Installation Subsidy",
        instrument_type=PolicyInstrumentType.ECONOMIC,
        target_behavior="Increase renewable energy adoption",
        compliance_mechanism="Rebate application process"
    )
    ```
    
    ### Voluntary Instruments
    ```python
    # Industry self-regulation
    sustainability_pledge = PolicyInstrument(
        label="Corporate Sustainability Commitment",
        instrument_type=PolicyInstrumentType.VOLUNTARY,
        target_behavior="Adopt sustainable business practices",
        compliance_mechanism="Self-reporting and peer review"
    )
    
    # Public-private partnership
    energy_efficiency_agreement = PolicyInstrument(
        label="Voluntary Energy Efficiency Agreement",
        instrument_type=PolicyInstrumentType.VOLUNTARY,
        target_behavior="Improve industrial energy efficiency",
        compliance_mechanism="Performance monitoring and recognition"
    )
    ```
    
    ### Information Instruments
    ```python
    # Public education campaign
    conservation_campaign = PolicyInstrument(
        label="Water Conservation Education Program",
        instrument_type=PolicyInstrumentType.INFORMATION,
        target_behavior="Reduce household water consumption",
        compliance_mechanism="Public awareness and social norms"
    )
    
    # Disclosure requirement
    environmental_reporting = PolicyInstrument(
        label="Corporate Environmental Disclosure",
        instrument_type=PolicyInstrumentType.INFORMATION,
        target_behavior="Increase transparency in environmental performance",
        compliance_mechanism="Mandatory reporting standards"
    )
    ```
    
    ## Policy Instrument Networks
    
    Complex policy problems often require multiple instrument types:
    
    ```python
    # Climate policy instrument mix
    regulatory_component = PolicyInstrument(
        label="Renewable Energy Standard",
        instrument_type=PolicyInstrumentType.REGULATORY
    )
    
    economic_component = PolicyInstrument(
        label="Carbon Pricing System", 
        instrument_type=PolicyInstrumentType.ECONOMIC
    )
    
    information_component = PolicyInstrument(
        label="Energy Efficiency Labeling",
        instrument_type=PolicyInstrumentType.INFORMATION
    )
    
    # Relationships showing instrument coordination
    coordinates_rel = Relationship(
        source_id=regulatory_component.id,
        target_id=economic_component.id,
        kind=RelationshipKind.COORDINATES_WITH
    )
    ```
    
    ## Integration with SFM Analysis
    
    PolicyInstrumentType enables:
    - **Implementation Analysis**: Understanding how policies are operationalized
    - **Effectiveness Assessment**: Evaluating instrument performance
    - **Design Optimization**: Selecting appropriate instruments for policy goals
    - **Institutional Mapping**: Connecting instruments to implementing organizations
    
    ## References
    
    - Hayden, F.G. (2006). "Policymaking for a Good Society", Chapter 8:
  Policy Instruments
    - Hood, C. (1983). "The Tools of Government"
    - Salamon, L.M. (2002). "The Tools of Government: A Guide to the New Governance"
    - Vedung, E. (1998). "Policy Instruments: Typologies and Theories"
    """
    REGULATORY = auto()  # Rules, regulations, legal requirements
    ECONOMIC = auto()  # Taxes, subsidies, market-based mechanisms
    VOLUNTARY = auto()  # Voluntary agreements, codes of conduct
    INFORMATION = auto()  # Education, disclosure, awareness campaigns


class ChangeType(Enum):
    """
    Classification of institutional and technological change patterns.

    Defines different modes of change that can occur in socio-economic systems,
    following institutional economics and innovation theory. Essential for understanding
    how institutions, technologies, and social systems evolve over time within
    Hayden's Social Fabric Matrix framework.
    
    ## Theoretical Background
    
    Change analysis in SFM recognizes that socio-economic systems undergo various
    types of transformation processes. Understanding change patterns is crucial for
    policy design, institutional development, and system intervention strategies.
    Hayden's framework emphasizes how different change types require different
    analytical approaches and policy responses.
    
    ## Core Change Types
    
    **EVOLUTIONARY**: Gradual, adaptive change through small variations
    **REVOLUTIONARY**: Rapid, disruptive transformation of system structure
    **CYCLICAL**: Recurring patterns of change following predictable cycles
    **INCREMENTAL**: Small, continuous improvements within existing frameworks
    
    ## Usage Examples
    
    ### Evolutionary Change Processes
    ```python
    # Gradual institutional adaptation
    market_evolution = ChangeProcess(
        label="Financial Market Evolution",
        change_type=ChangeType.EVOLUTIONARY,
        description="Gradual adaptation of financial regulations to new technologies",
        success_probability=0.75
    )
    
    # Technology adoption process
    digital_transformation = ChangeProcess(
        label="Digital Government Services",
        change_type=ChangeType.EVOLUTIONARY,
        description="Gradual digitization of government service delivery",
        change_agents=[government_agency.id, technology_vendor.id]
    )
    ```
    
    ### Revolutionary Change Processes
    ```python
    # Disruptive institutional change
    regulatory_overhaul = ChangeProcess(
        label="Financial Sector Deregulation",
        change_type=ChangeType.REVOLUTIONARY,
        description="Fundamental restructuring of financial regulatory framework",
        success_probability=0.40,
        resistance_factors=[incumbent_institutions.id, regulatory_culture.id]
    )
    
    # Technological disruption
    ai_automation = ChangeProcess(
        label="AI-Driven Process Automation",
        change_type=ChangeType.REVOLUTIONARY,
        description="Fundamental transformation of work processes through AI",
        change_trajectory=[current_state, transition_state, future_state]
    )
    ```
    
    ### Cyclical Change Processes
    ```python
    # Economic cycles
    business_cycle = ChangeProcess(
        label="Economic Business Cycle",
        change_type=ChangeType.CYCLICAL,
        description="Recurring patterns of economic expansion and contraction",
        change_trajectory=[expansion, peak, contraction, trough]
    )
    
    # Political cycles
    electoral_cycle = ChangeProcess(
        label="Electoral Policy Cycle",
        change_type=ChangeType.CYCLICAL,
        description="Policy changes following electoral patterns",
        success_probability=0.85
    )
    ```
    
    ### Incremental Change Processes
    ```python
    # Continuous improvement
    efficiency_improvement = ChangeProcess(
        label="Operational Efficiency Enhancement",
        change_type=ChangeType.INCREMENTAL,
        description="Ongoing small improvements to operational processes",
        success_probability=0.90,
        change_agents=[management_team.id, operations_staff.id]
    )
    
    # Policy fine-tuning
    regulation_adjustment = ChangeProcess(
        label="Regulatory Parameter Adjustment",
        change_type=ChangeType.INCREMENTAL,
        description="Minor adjustments to regulatory requirements",
        resistance_factors=[]  # Minimal resistance for small changes
    )
    ```
    
    ## Change Process Integration
    
    ChangeType integrates with other SFM components:
    
    ### With Institutions and Actors
    ```python
    # Institutional change with actor involvement
    institution = Institution(
        label="Environmental Protection Agency",
        layer=InstitutionLayer.ORGANIZATION
    )
    
    change_agent = Actor(
        label="Environmental Activist Group",
        sector="Non-profit"
    )
    
    institutional_reform = ChangeProcess(
        label="EPA Mandate Expansion",
        change_type=ChangeType.EVOLUTIONARY,
        change_agents=[change_agent.id],
        description="Gradual expansion of environmental protection authority"
    )
    
    # Relationship showing change influence
    influences_rel = Relationship(
        source_id=change_agent.id,
        target_id=institution.id,
        kind=RelationshipKind.INFLUENCES,
        description="Advocacy influence on institutional change"
    )
    ```
    
    ### With Policy Instruments
    ```python
    # Policy change with instrument modification
    old_policy = PolicyInstrument(
        label="Traditional Command-Control Regulation",
        instrument_type=PolicyInstrumentType.REGULATORY
    )
    
    new_policy = PolicyInstrument(
        label="Market-Based Environmental Policy",
        instrument_type=PolicyInstrumentType.ECONOMIC
    )
    
    policy_transition = ChangeProcess(
        label="Regulatory Instrument Shift",
        change_type=ChangeType.EVOLUTIONARY,
        description="Transition from command-control to market-based regulation"
    )
    
    # Relationships showing policy evolution
    transforms_rel = Relationship(
        source_id=policy_transition.id,
        target_id=old_policy.id,
        kind=RelationshipKind.TRANSFORMS
    )
    ```
    
    ## Change Analysis Patterns
    
    Different change types require different analytical approaches:
    
    - **Evolutionary**: Focus on adaptation mechanisms and gradual feedback
    - **Revolutionary**: Analyze disruption sources and transformation triggers  
    - **Cyclical**: Identify cycle patterns and timing factors
    - **Incremental**: Track cumulative effects and optimization processes
    
    ## Integration with Temporal Dynamics
    
    ChangeType works with temporal analysis:
    
    ```python
    # Change process with temporal tracking
    institutional_change = ChangeProcess(
        label="Healthcare System Reform",
        change_type=ChangeType.EVOLUTIONARY,
        change_trajectory=[
            TimeSlice(label="Pre-reform"),
            TimeSlice(label="Implementation"),
            TimeSlice(label="Post-reform")
        ],
        temporal_dynamics=TemporalDynamics(
            # Detailed time-based analysis
        )
    )
    ```
    
    ## References
    
    - Hayden, F.G. (2006). "Policymaking for a Good Society", Chapter 9:
  Institutional Change
    - North, D.C. (1990). "Institutions, Institutional Change and Economic Performance"
    - Arthur, W.B. (1994). "Increasing Returns and Path Dependence in the Economy"
    - Pierson, P. (2000). "Increasing Returns, Path Dependence, and the Study
  of Politics"
    - Commons, J.R. (1924). "Legal Foundations of Capitalism", Chapter 7: Going Concerns
    """
    EVOLUTIONARY = auto()  # Gradual, adaptive change
    REVOLUTIONARY = auto()  # Rapid, disruptive transformation
    CYCLICAL = auto()  # Recurring patterns of change
    INCREMENTAL = auto()  # Small, continuous improvements


class BehaviorPatternType(Enum):
    """
    Classification of behavioral patterns in Social Fabric Matrix analysis.

    Categorizes recurring patterns of behavior that actors exhibit in
    socio-economic systems, particularly relevant to Hayden's analysis of
    ceremonial versus instrumental behavior patterns that shape institutional
    dynamics and economic outcomes.
    
    ## Theoretical Background
    
    Hayden's institutional analysis distinguishes between different behavioral
    patterns that either support or hinder adaptive institutional development.
    Understanding these patterns is crucial for predicting institutional change
    and designing effective policy interventions.
    
    ## Core Behavior Patterns
    
    - **HABITUAL**: Routine, unconscious behaviors following established patterns
    - **STRATEGIC**: Deliberate, goal-oriented behaviors with explicit objectives
    - **ADAPTIVE**: Flexible, responsive behaviors that adjust to changing conditions
    - **RESISTANT**: Change-resistant, conservative behaviors that maintain status quo
    
    ## Usage Examples
    
    ```python
    # Habitual behavior pattern
    routine_compliance = BehaviorPattern(
        label="Standard Regulatory Compliance",
        pattern_type=BehaviorPatternType.HABITUAL,
        description="Routine following of established regulatory procedures"
    )
    
    # Strategic behavior pattern
    market_positioning = BehaviorPattern(
        label="Competitive Market Strategy",
        pattern_type=BehaviorPatternType.STRATEGIC,
        description="Deliberate positioning for market advantage"
    )
    
    # Adaptive behavior pattern
    crisis_response = BehaviorPattern(
        label="Crisis Adaptation Response",
        pattern_type=BehaviorPatternType.ADAPTIVE,
        description="Flexible adjustment to emergency conditions"
    )
    ```
    """
    HABITUAL = auto()  # Routine, unconscious behaviors
    STRATEGIC = auto()  # Deliberate, goal-oriented behaviors
    ADAPTIVE = auto()  # Flexible, responsive behaviors
    RESISTANT = auto()  # Change-resistant, conservative behaviors


class FeedbackPolarity(Enum):
    """
    Classification of feedback loop polarity in system dynamics.

    Defines whether a feedback loop reinforces or balances system behavior.
    Essential for understanding system stability, growth patterns, and
    intervention points in Social Fabric Matrix analysis.
    
    ## Usage Examples
    
    ```python
    # Reinforcing feedback (amplifies change)
    growth_feedback = Feedback(
        label="Economic Growth Feedback",
        polarity=FeedbackPolarity.REINFORCING,
        description="Investment leads to growth, which attracts more investment"
    )
    
    # Balancing feedback (stabilizes system)  
    regulatory_feedback = Feedback(
        label="Market Regulation Feedback",
        polarity=FeedbackPolarity.BALANCING,
        description="Market excess triggers regulatory response"
    )
    ```
    """
    REINFORCING = auto()  # Amplifies or accelerates change (positive feedback)
    BALANCING = auto()  # Stabilizes or counteracts change (negative feedback)


class FeedbackType(Enum):
    """
    Classification of feedback types by directional impact.

    Categorizes feedback effects based on their directional influence
    on system behavior.
    """
    POSITIVE = auto()  # Enhancing, amplifying feedback
    NEGATIVE = auto()  # Dampening, correcting feedback
    NEUTRAL = auto()  # Balanced or minimal feedback


class TemporalFunctionType(Enum):
    """
    Classification of temporal function types for modeling change over time.

    Defines mathematical functions used to model how values change
    over time in temporal dynamics analysis.
    """
    LINEAR = auto()  # Constant rate of change
    EXPONENTIAL = auto()  # Accelerating or decelerating change
    LOGISTIC = auto()  # S-curve growth with limits
    CYCLICAL = auto()  # Periodic, repeating patterns
    STEP = auto()  # Discrete jumps or threshold changes
    RANDOM = auto()  # Stochastic or unpredictable changes


class ValidationRuleType(Enum):
    """
    Classification of validation rule types for data integrity.

    Defines different types of validation rules that can be applied
    to ensure data quality and consistency.
    """
    RANGE = auto()  # Value within specified bounds
    SUM = auto()  # Sum constraints across multiple values
    REQUIRED = auto()  # Mandatory field validation
    UNIQUE = auto()  # Uniqueness constraints
    FORMAT = auto()  # Format or pattern validation
    RELATIONSHIP = auto()  # Cross-field relationship validation


class SystemPropertyType(Enum):
    """
    Classification of system-level property types in SFM analysis.

    Defines different categories of system-level metrics and properties
    that can be measured and tracked in Social Fabric Matrix systems.
    Essential for evaluating overall system performance, health, and
    development outcomes in institutional analysis.
    
    ## Usage Examples
    
    ```python
    # Structural system property
    network_density = SystemProperty(
        label="Institutional Network Density",
        property_type=SystemPropertyType.STRUCTURAL,
        value=0.65,
        unit="density_ratio",
        description="Measure of interconnectedness in institutional network"
    )
    
    # Performance system property
    policy_effectiveness = SystemProperty(
        label="Policy Implementation Effectiveness",
        property_type=SystemPropertyType.PERFORMANCE,
        value=78.5,
        unit="percentage",
        description="Overall effectiveness of policy implementation"
    )
    
    # Sustainability system property
    resource_efficiency = SystemProperty(
        label="Resource Use Efficiency",
        property_type=SystemPropertyType.SUSTAINABILITY,
        value=0.82,
        unit="efficiency_index",
        description="Long-term sustainability of resource utilization"
    )
    ```
    """
    STRUCTURAL = auto()  # Network structure properties
    DYNAMIC = auto()  # Temporal behavior properties
    PERFORMANCE = auto()  # Efficiency and effectiveness metrics
    RESILIENCE = auto()  # Adaptive capacity and robustness
    EQUITY = auto()  # Distributional fairness metrics
    SUSTAINABILITY = auto()  # Long-term viability indicators


class RelationshipKind(Enum):
    """
    Taxonomy of relationship types in Social Fabric Matrix systems.

    Defines the various ways actors, institutions, resources, and processes can be
    related to each other in Hayden's institutional analysis framework. This
comprehensive
    taxonomy enables detailed mapping of institutional dependencies, resource flows,
    power relationships, and system dynamics essential for SFM analysis.
    
    ## Theoretical Foundation
    
    Relationship analysis in SFM recognizes that socio-economic systems are
fundamentally
    structured by relationships between actors, institutions, and resources. Hayden's
    framework emphasizes how these relationships create patterns of coordination,
    dependency, and power that shape economic outcomes and social welfare.
    
    ## Core Relationship Categories
    
    **Governance Relationships**: Authority, regulation, and institutional control
    **Resource Flow Relationships**: Economic exchanges and resource movements  
    **Knowledge Relationships**: Information transfer and learning processes
    **Social Relationships**: Collaboration, coordination, and mutual support
    **Influence Relationships**: Power dynamics and behavioral modification
    
    ## Usage Examples
    
    ### Governance and Authority Relationships
    ```python
    # Government regulatory authority
    epa = Actor(label="EPA", sector="Government")
    chemical_company = Actor(label="Chemical Manufacturer", sector="Industry")
    
    regulatory_rel = Relationship(
        source_id=epa.id,
        target_id=chemical_company.id,
        kind=RelationshipKind.REGULATES,
        description="Environmental compliance oversight"
    )
    
    # Policy implementation
    city_government = Actor(label="City Government", sector="Public")
    zoning_policy = Policy(label="Zoning Regulations", authority="City")
    
    enacts_rel = Relationship(
        source_id=city_government.id,
        target_id=zoning_policy.id,
        kind=RelationshipKind.ENACTS,
        description="Local zoning law creation"
    )
    ```
    
    ### Economic and Resource Flow Relationships
    ```python
    # Supply chain relationships
    supplier = Actor(label="Raw Material Supplier", sector="Industry")
    manufacturer = Actor(label="Manufacturer", sector="Industry")
    
    supply_rel = Relationship(
        source_id=supplier.id,
        target_id=manufacturer.id,
        kind=RelationshipKind.SUPPLIES,
        description="Raw material provision"
    )
    
    # Financial relationships
    bank = Actor(label="Development Bank", sector="Financial")
    startup = Actor(label="Green Tech Startup", sector="Technology")
    
    funding_rel = Relationship(
        source_id=bank.id,
        target_id=startup.id,
        kind=RelationshipKind.FUNDS,
        description="Venture capital investment"
    )
    
    # Resource transformation
    solar_panel = Resource(label="Solar Panel", rtype=ResourceType.PRODUCED)
    electricity = Resource(label="Electrical Energy", rtype=ResourceType.RENEWABLE)
    
    conversion_rel = Relationship(
        source_id=solar_panel.id,
        target_id=electricity.id,
        kind=RelationshipKind.CONVERTS,
        description="Solar energy conversion"
    )
    ```
    
    ### Knowledge and Information Relationships
    ```python
    # Research and education
    university = Actor(label="State University", sector="Education")
    students = Actor(label="Graduate Students", sector="Education")
    
    education_rel = Relationship(
        source_id=university.id,
        target_id=students.id,
        kind=RelationshipKind.EDUCATES,
        description="Graduate degree programs"
    )
    
    # Information flow
    weather_service = Actor(label="National Weather Service", sector="Government")
    farmers = Actor(label="Agricultural Producers", sector="Agriculture")
    
    info_rel = Relationship(
        source_id=weather_service.id,
        target_id=farmers.id,
        kind=RelationshipKind.INFORMS,
        description="Weather forecast provision"
    )
    ```
    
    ### Social and Collaborative Relationships
    ```python
    # Multi-stakeholder collaboration
    ngo = Actor(label="Environmental NGO", sector="Non-profit")
    industry_group = Actor(label="Industry Association", sector="Private")
    
    collab_rel = Relationship(
        source_id=ngo.id,
        target_id=industry_group.id,
        kind=RelationshipKind.COLLABORATES_WITH,
        description="Sustainability initiative partnership"
    )
    
    # Advocacy relationships
    consumer_group = Actor(label="Consumer Advocacy Group", sector="Non-profit")
    renewable_energy = Policy(label="Renewable Energy Policy", authority="State")
    
    advocacy_rel = Relationship(
        source_id=consumer_group.id,
        target_id=renewable_energy.id,
        kind=RelationshipKind.ADVOCATES_FOR,
        description="Policy support campaign"
    )
    ```
    
    ## Complex Relationship Networks
    
    ### Multi-Actor Policy Networks
    ```python
    # Create network of relationships around policy issue
    federal_agency = Actor(label="Federal Environmental Agency")
    state_agency = Actor(label="State Environmental Department") 
    local_government = Actor(label="City Council")
    industry = Actor(label="Manufacturing Industry")
    citizens = Actor(label="Local Citizens")
    
    # Hierarchical governance relationships
    mandate_rel = Relationship(
        source_id=federal_agency.id,
        target_id=state_agency.id,
        kind=RelationshipKind.MANDATES
    )
    
    delegate_rel = Relationship(
        source_id=state_agency.id,
        target_id=local_government.id,
        kind=RelationshipKind.DELEGATES
    )
    
    # Regulatory relationships
    regulate_rel = Relationship(
        source_id=local_government.id,
        target_id=industry.id,
        kind=RelationshipKind.REGULATES
    )
    
    # Accountability relationships
    account_rel = Relationship(
        source_id=local_government.id,
        target_id=citizens.id,
        kind=RelationshipKind.ACCOUNTABLE_TO
    )
    ```
    
    ## Relationship Direction and Symmetry
    
    Most relationships in SFM are **directional**, indicating flow or influence from
    source to target:
    
    - **GOVERNS**: Authority flows from government to governed entity
    - **SUPPLIES**: Resources flow from supplier to recipient
    - **INFLUENCES**: Impact flows from influencer to influenced
    
    Some relationships can be **bidirectional** or **symmetric**:
    
    - **COLLABORATES_WITH**: Mutual cooperation
    - **EXCHANGES_WITH**: Mutual exchange
    - **COMPETES_WITH**: Mutual rivalry
    
    ## Integration with Flow Analysis
    
    Relationships often involve specific flows that can be tracked:
    
    ```python
    # Relationship with associated flows
    payment_flow = Flow(
        label="Service Payment",
        nature=FlowNature.FINANCIAL,
        flow_type=FlowType.FINANCIAL
    )
    
    service_rel = Relationship(
        source_id=client.id,
        target_id=service_provider.id,
        kind=RelationshipKind.PAYS,
        flows=[payment_flow.id]  # Link specific flows to relationship
    )
    ```
    
    ## Hayden-Specific Institutional Relationships
    
    The taxonomy includes relationships particularly relevant to Hayden's analysis:
    
    - **REINFORCES/UNDERMINES**: Feedback relationships for institutional stability
    - **TRANSFORMS**: Fundamental institutional change relationships
    - **ENABLES/CONSTRAINS**: Capacity and limitation relationships
    - **LEGITIMIZES**: Authority and acceptance relationships
    
    ## Validation and Compatibility
    
    RelationshipKind works with validation systems to ensure logical consistency:
    
    ```python
    # Valid government-to-institution relationship
    governs_rel = Relationship(
        source_id=government_actor.id,
        target_id=regulated_institution.id,
        kind=RelationshipKind.GOVERNS  # Appropriate for this actor-institution pairing
    )
    
    # Validation will check compatibility of relationship type with actor types
    ```
    
    ## References
    
    - Hayden, F.G. (2006). "Policymaking for a Good Society", Chapter 7:
  Institutional Relationships
    - Hayden, F.G. (1982). "Social Fabric Matrix: From Perspective to Analytical Tool"
    - Commons, J.R. (1924). "Legal Foundations of Capitalism", Chapter 5:
  The Institutional Economics of Legal Rights
    - Mitchell, W.C. (1937). "The Backward Art of Spending Money", Chapter 3:
  Institutional Analysis
    """
    # Governance and Authority Relationships
    GOVERNS = auto()  # Authority over another entity
    REGULATES = auto()  # Creates or enforces rules for
    AUTHORIZES = auto()  # Grants permission to
    MANDATES = auto()  # Makes actions compulsory
    ENFORCES = auto()  # Ensures compliance with rules
    DELEGATES = auto()  # Transfers authority to
    REPRESENTS = auto()  # Acts on behalf of
    MONITORS = auto()  # Observes and assesses
    ACCOUNTABLE_TO = auto()  # Must answer to
    LICENSES = auto()  # Formally permits activity
    CERTIFIES = auto()  # Validates compliance or quality
    SANCTIONS = auto()  # Penalizes for non-compliance
    REINFORCES = auto()  # Positive feedback relationship
    UNDERMINES = auto()  # Negative feedback relationship
    AFFECTS = auto()  # Base Feedback relationship
    ENACTS = auto()  # Creates or modifies laws, policies, or regulations

    # Resource Flow Relationships
    FUNDS = auto()  # Provides money to
    PAYS = auto()  # Exchanges money for goods/services
    ALLOCATES = auto()  # Distributes resources to
    TRANSFERS = auto()  # Moves resources without transformation
    EXTRACTS = auto()  # Removes resources from
    CONSUMES = auto()  # Uses up resources from
    PRODUCES = auto()  # Creates outputs for
    DISTRIBUTES = auto()  # Disseminates to multiple targets
    STORES = auto()  # Holds resources for
    CONVERTS = auto()  # Transforms one resource to another
    RECYCLES = auto()  # Reprocesses for reuse

    # Economic and Market Relationships
    BUYS_FROM = auto()  # Purchases goods/services
    SELLS_TO = auto()  # Provides goods/services for payment
    COMPETES_WITH = auto()  # Rivals for resources or markets
    SUPPLIES = auto()  # Provides inputs to
    EMPLOYS = auto()  # Hires for labor
    CONTRACTS_WITH = auto()  # Formal agreement for exchange
    INVESTS_IN = auto()  # Commits resources for future return
    INSURES = auto()  # Provides risk protection for
    SUBSIDIZES = auto()  # Provides financial support to
    TAXES = auto()  # Collects mandatory payment from
    RENTS_TO = auto()  # Provides temporary use rights
    OWNS = auto()  # Has property rights over
    EXCHANGES_WITH = auto()  # Actor-to-actor transfer

    # Knowledge and Information Relationships
    INFORMS = auto()  # Provides information to
    ADVISES = auto()  # Gives guidance to
    EDUCATES = auto()  # Transfers knowledge to
    RESEARCHES = auto()  # Investigates for
    INNOVATES_FOR = auto()  # Creates new solutions for
    DOCUMENTS = auto()  # Records information about
    ANALYZES = auto()  # Examines and interprets
    FORECASTS = auto()  # Predicts outcomes for
    COMMUNICATES_WITH = auto()  # Exchanges information with
    MEASURES = auto()  # Quantifies attributes of
    CALCULATES = auto()  # Computes values related to

    # Social and Collaborative Relationships
    COLLABORATES_WITH = auto()  # Works jointly with
    SERVES = auto()  # Provides services to
    SUPPORTS = auto()  # Helps or assists
    PARTICIPATES_IN = auto()  # Takes part in
    ALLIES_WITH = auto()  # Forms strategic partnership with
    COORDINATES_WITH = auto()  # Aligns activities with
    FACILITATES = auto()  # Makes easier or enables
    MEDIATES = auto()  # Resolves conflicts between
    ADVOCATES_FOR = auto()  # Publicly supports
    ORGANIZES = auto()  # Arranges or structures
    CONVENES = auto()  # Brings together

    # Influence and Impact Relationships
    INFLUENCES = auto()  # Affects decisions or behavior of
    CONSTRAINS = auto()  # Limits actions of
    ENABLES = auto()  # Makes possible actions of
    INCENTIVIZES = auto()  # Motivates specific behaviors
    DISCOURAGES = auto()  # Deters specific behaviors
    SHAPES = auto()  # Molds or forms
    STRENGTHENS = auto()  # Increases capacity of
    WEAKENS = auto()  # Diminishes capacity of
    DISRUPTS = auto()  # Causes discontinuity in
    STABILIZES = auto()  # Maintains equilibrium of
    TRANSFORMS = auto()  # Fundamentally changes

    # Process and Operational Relationships
    IMPLEMENTS = auto()  # Puts into practice
    OPERATES = auto()  # Runs or manages
    MAINTAINS = auto()  # Keeps in working order
    TESTS = auto()  # Evaluates performance of
    INSTALLS = auto()  # Sets up for use
    TRANSPORTS = auto()  # Moves from one location to another
    INTEGRATES = auto()  # Combines into system
    OPTIMIZES = auto()  # Improves efficiency of
    AUTOMATES = auto()  # Makes self-operating
    REPAIRS = auto()  # Fixes or restores
    SOLVES = auto()  # Addresses problems or challenges
    USES = auto()  # Actor/process employs a resource or technology

    # Structural and Containment Relationships
    CONTAINS = auto()  # Has as a component
    BELONGS_TO = auto()  # Is a member of
    CONNECTS = auto()  # Links physically or logically
    COMPOSED_OF = auto()  # Consists of
    CATEGORIZES = auto()  # Places in classification
    AGGREGATES = auto()  # Combines into a whole
    SEPARATES = auto()  # Divides or keeps apart
    HOSTS = auto()  # Provides environment for
    ATTACHES_TO = auto()  # Joins or fixes to
    EMBEDS_WITHIN = auto()  # Incorporates deeply into
    ENCOMPASSES = auto()  # Includes completely
    LOCATED_IN = auto()  # Spatial anchoring

    # Temporal and Sequential Relationships
    PRECEDES = auto()  # Comes before
    FOLLOWS = auto()  # Comes after
    TRIGGERS = auto()  # Initiates or causes
    SYNCHRONIZES_WITH = auto()  # Coordinates timing with
    DELAYS = auto()  # Postpones or slows
    ACCELERATES = auto()  # Speeds up
    SCHEDULES = auto()  # Sets timing for
    ITERATES = auto()  # Repeats process with
    SUPERSEDES = auto()  # Replaces or makes obsolete
    RENEWS = auto()  # Extends or refreshes
    TERMINATES = auto()  # Ends relationship with
    OCCURS_DURING = auto()  # Temporal anchoring
    ENABLES_FUTURE = auto()
    CONSTRAINS_FUTURE = auto()

    # Environmental and Ecological Relationships
    SUSTAINS = auto()  # Maintains viability of
    POLLUTES = auto()  # Degrades quality of
    CONSERVES = auto()  # Uses carefully to prevent depletion
    RESTORES = auto()  # Returns to previous condition
    ADAPTS_TO = auto()  # Changes in response to
    MITIGATES = auto()  # Reduces negative impact on
    DEPENDS_ON = auto()  # Requires for functioning
    COEXISTS_WITH = auto()  # Lives alongside without harm
    HARVESTS = auto()  # Collects resources from
    PROCESSES = auto()  # Treats or handles materials from
    CULTIVATES = auto()  # Grows or nurtures

    # Development and Change Relationships
    DEVELOPS = auto()  # Creates growth or maturity in
    EXPANDS = auto()  # Increases size or scope of
    CONTRACTS = auto()  # Decreases size or scope of
    REDESIGNS = auto()  # Changes structure or function of
    EVOLVES_WITH = auto()  # Changes in mutual response with
    EMERGES_FROM = auto()  # Comes into existence from
    TRANSITIONS_TO = auto()  # Changes state to become
    CONSTRUCTS = auto()  # Builds or creates
    DEMOLISHES = auto()  # Tears down or removes
    UPGRADES = auto()  # Improves quality or function of
    CUSTOMIZES = auto()  # Modifies to suit specific needs
    INHIBITS = auto()  # Limiting or constraining relationship

    # Belief and Value Relationships
    VALUES = auto()  # Holds in high regard
    TRUSTS = auto()  # Has confidence in
    PERCEIVES = auto()  # Forms mental impression of
    INTERPRETS = auto()  # Ascribes meaning to
    CHALLENGES = auto()  # Questions validity of
    ACCEPTS = auto()  # Receives as valid or appropriate
    REJECTS = auto()  # Refuses to accept
    NORMALIZES = auto()  # Makes conform to standard
    PRIORITIZES = auto()  # Gives precedence to
    ALIGNS_WITH = auto()  # Positions in agreement with
    DISAGREES_WITH = auto()  # Holds contrary views to
    BELIEVES_IN = auto()  # Holds a conviction about

    # Hayden-specific relationships
    LEGITIMIZES = auto()
    DELEGITIMIZES = auto()
    CEREMONIALLY_REINFORCES = auto()
    INSTRUMENTALLY_ADAPTS = auto()
    CREATES_PATH_DEPENDENCY = auto()
    ENABLES_INNOVATION = auto()
    DISTRIBUTES_POWER = auto()
    CONCENTRATES_POWER = auto()
    BENEFITS_FROM = auto()  # Gains advantage or support from

    @property
    def ceremonial_tendency(self) -> float:
        """
        Returns a value from 0.0-1.0 indicating ceremonial vs instrumental nature.

        Based on Hayden's SFM framework distinction between ceremonial and instrumental
        behaviors. 0.0 = purely instrumental (problem-solving, adaptive),
        1.0 = purely ceremonial (status-preserving, traditional).

        Returns:
            float: Ceremonial tendency score from 0.0 (instrumental) to 1.0 (ceremonial)
        """
        # Mapping of relationship types to their ceremonial tendency
        ceremonial_tendencies = {
            # Highly ceremonial relationships (0.8-1.0) - status, tradition, hierarchy
            RelationshipKind.CEREMONIALLY_REINFORCES: 0.95,
            RelationshipKind.LEGITIMIZES: 0.85,
            RelationshipKind.GOVERNS: 0.75,
            RelationshipKind.AUTHORIZES: 0.75,
            RelationshipKind.MANDATES: 0.75,
            RelationshipKind.REPRESENTS: 0.70,
            RelationshipKind.SANCTIONS: 0.80,
            RelationshipKind.VALUES: 0.85,
            RelationshipKind.TRUSTS: 0.70,
            RelationshipKind.BELIEVES_IN: 0.80,
            RelationshipKind.NORMALIZES: 0.75,
            RelationshipKind.PRIORITIZES: 0.70,

            # Moderately ceremonial (0.5-0.8) - mixed institutional/adaptive
            RelationshipKind.REGULATES: 0.65,
            RelationshipKind.ENFORCES: 0.65,
            RelationshipKind.DELEGATES: 0.60,
            RelationshipKind.MONITORS: 0.55,
            RelationshipKind.LICENSES: 0.60,
            RelationshipKind.CERTIFIES: 0.55,
            RelationshipKind.REINFORCES: 0.60,
            RelationshipKind.ALIGNS_WITH: 0.55,
            RelationshipKind.ACCEPTS: 0.55,
            RelationshipKind.INTERPRETS: 0.50,

            # Moderately instrumental (0.2-0.5) - some adaptation with structure
            RelationshipKind.ADVISES: 0.45,
            RelationshipKind.EDUCATES: 0.40,
            RelationshipKind.INFORMS: 0.35,
            RelationshipKind.ANALYZES: 0.30,
            RelationshipKind.MEASURES: 0.25,
            RelationshipKind.CALCULATES: 0.20,
            RelationshipKind.RESEARCHES: 0.30,
            RelationshipKind.INNOVATES_FOR: 0.25,
            RelationshipKind.DEVELOPS: 0.35,
            RelationshipKind.EVOLVES_WITH: 0.40,
            RelationshipKind.ADAPTS_TO: 0.35,

            # Highly instrumental (0.0-0.2) - problem-solving, adaptive, productive
            RelationshipKind.INSTRUMENTALLY_ADAPTS: 0.05,
            RelationshipKind.PRODUCES: 0.15,
            RelationshipKind.PROCESSES: 0.10,
            RelationshipKind.CONVERTS: 0.10,
            RelationshipKind.CONSTRUCTS: 0.15,
            RelationshipKind.OPERATES: 0.15,
            RelationshipKind.MAINTAINS: 0.20,
            RelationshipKind.REPAIRS: 0.15,
            RelationshipKind.UPGRADES: 0.20,
            RelationshipKind.CUSTOMIZES: 0.15,
            RelationshipKind.ENABLES_INNOVATION: 0.10,
            RelationshipKind.SOLVES: 0.05,

            # Economic relationships - moderately instrumental (0.3-0.6)
            RelationshipKind.EXCHANGES_WITH: 0.40,
            RelationshipKind.BUYS_FROM: 0.35,
            RelationshipKind.SELLS_TO: 0.35,
            RelationshipKind.INVESTS_IN: 0.45,
            RelationshipKind.EMPLOYS: 0.50,
            RelationshipKind.CONTRACTS_WITH: 0.45,
            RelationshipKind.FUNDS: 0.40,
            RelationshipKind.PAYS: 0.30,
            RelationshipKind.ALLOCATES: 0.45,
            RelationshipKind.DISTRIBUTES: 0.40,
        }

        # Return the mapped value, or default to moderate (0.5) if not explicitly mapped
        return ceremonial_tendencies.get(self, 0.5)


class PowerResourceType(Enum):
    """
    Classification of power resource types in Social Fabric Matrix analysis.

    Based on Hayden's analysis of power dynamics within institutional systems,
    representing different forms of power and control that actors can wield
    to influence outcomes and maintain or change institutional arrangements.
    """
    INSTITUTIONAL_AUTHORITY = auto()  # Formal authority roles and positions
    ECONOMIC_CONTROL = auto()  # Control over financial resources and economic flows
    INFORMATION_ACCESS = auto()  # Access to and control of information and knowledge
    NETWORK_POSITION = auto()  # Strategic position within networks
    CULTURAL_LEGITIMACY = auto()  # Cultural authority and legitimacy sources


class ToolSkillTechnologyType(Enum):
    """
    Classification of tool-skill-technology complex components.

    Represents Hayden's concept of the tool-skill-technology complex as integrated
    systems where physical tools, human skills, and technological knowledge
    combine to enable instrumental problem-solving capabilities.
    """
    PHYSICAL_TOOL = auto()  # Material instruments and devices
    COGNITIVE_SKILL = auto()  # Mental capabilities and knowledge
    TECHNOLOGY_SYSTEM = auto()  # Integrated technological arrangements
    TECHNIQUE = auto()  # Specific methods and procedures
    METHODOLOGY = auto()  # Systematic approaches and frameworks
    CRAFT_KNOWLEDGE = auto()  # Embodied practical knowledge
    DIGITAL_CAPABILITY = auto()  # Digital tools and skills
    ANALYTICAL_METHOD = auto()  # Formal analytical techniques
    PROBLEM_SOLVING_APPROACH = auto()  # General problem-solving strategies
    INNOVATION_CAPACITY = auto()  # Capability to create new solutions


class PathDependencyType(Enum):
    """
    Classification of path dependency strength in institutional systems.

    Represents the degree to which institutional arrangements become locked-in
    and resistant to change due to historical patterns, sunk costs, and
    reinforcing mechanisms.
    """
    WEAK = auto()  # Easy to change, low switching costs, flexible arrangements
    MODERATE = auto()  # Some resistance to change, moderate switching costs
    STRONG = auto()  # High resistance to change, significant switching costs
    LOCKED_IN = auto()  # Extremely difficult to change, path dependency dominates


class InstitutionalChangeType(Enum):
    """
    Classification of institutional change mechanisms and patterns.

    Represents different modes and patterns through which institutional
    arrangements evolve, transform, or maintain stability over time.
    """
    INCREMENTAL = auto()  # Gradual, small-scale adjustments
    TRANSFORMATIONAL = auto()  # Significant structural changes
    REVOLUTIONARY = auto()  # Rapid, fundamental system overhaul
    EVOLUTIONARY = auto()  # Organic adaptation over time
    ADAPTIVE = auto()  # Responsive changes to environmental pressures
    CRISIS_DRIVEN = auto()  # Changes triggered by system crises
    INNOVATION_LED = auto()  # Changes driven by technological or social innovation
    REFORM_BASED = auto()  # Planned, policy-driven changes
    EMERGENT = auto()  # Bottom-up, spontaneous changes
    CYCLICAL = auto()  # Recurring patterns of change and stability


class TechnologyReadinessLevel(Enum):
    """
    NASA Technology Readiness Levels adapted for Social Fabric Matrix analysis.

    Provides a systematic metric for assessing the maturity of technologies
    within socio-economic systems, following NASA's TRL framework but adapted
    for Hayden's tool-skill-technology complex analysis.

    Based on:
    - NASA Technology Readiness Assessment (TRA) Guidance
    - Hayden's analysis of technological systems in SFM framework
    - Institutional economics perspectives on technology adoption
    """
    BASIC_PRINCIPLES = 1        # Basic principles observed and reported
    TECHNOLOGY_CONCEPT = 2      # Technology concept and/or application formulated
    EXPERIMENTAL_PROOF = 3      # Experimental proof of concept
    LABORATORY_VALIDATION = 4   # Component validation in laboratory
    RELEVANT_ENVIRONMENT = 5    # Component validation in relevant env
    DEMONSTRATION = 6           # System demonstration in relevant env
    PROTOTYPE_DEMONSTRATION = 7 # Prototype demo in operational env
    SYSTEM_COMPLETE = 8         # System completed and qualified
    ACTUAL_SYSTEM = 9          # System proven through successful missions


class LegitimacySource(Enum):
    """
    Weber's types of authority and legitimacy sources adapted for SFM analysis.

    Based on Max Weber's tripartite classification of authority types,
    extended with additional sources relevant to contemporary institutional
    analysis within Social Fabric Matrix framework.

    References:
    - Weber, M. "Economy and Society" - three pure types of legitimate domination
    - Hayden's analysis of legitimacy in institutional systems
    - Contemporary institutional theory on authority and legitimacy
    """
    TRADITIONAL = auto()        # Custom, precedent, established traditions
    CHARISMATIC = auto()        # Personal qualities - exceptional individual
    LEGAL_RATIONAL = auto()     # Rules, procedures - impersonal order
    EXPERT = auto()            # Technical knowledge and competence
    DEMOCRATIC = auto()         # Popular consent and participation


# ───────────────────────────────────────────────
# ERROR HANDLING AND VALIDATION
# ───────────────────────────────────────────────


class SFMEnumError(Exception):
    """Base exception for SFM enum-related errors."""


class IncompatibleEnumError(SFMEnumError):
    """Raised when incompatible enum values are used together."""


class InvalidEnumOperationError(SFMEnumError):
    """Raised when an invalid operation is attempted on enum values."""


class EnumValidator:
    """Validates enum values and combinations for SFM consistency."""

    # Define node type mappings - these correspond to the actual model classes
    ACTOR_TYPES = {'Actor'}
    INSTITUTION_TYPES = {'Institution', 'Policy'}
    RESOURCE_TYPES = {'Resource'}
    PROCESS_TYPES = {'Process', 'Flow'}
    SYSTEM_TYPES = {'TechnologySystem', 'BeliefSystem', 'ValueSystem'}
    OTHER_TYPES = {'FeedbackLoop', 'Indicator', 'AnalyticalContext', 'SystemProperty',
                   'CeremonialBehavior', 'InstrumentalBehavior', 'PolicyInstrument'}

    # Define relationship context rules
    RELATIONSHIP_RULES: Dict[RelationshipKind, Dict[str, Union[List[Tuple[str, str]], str]]] = {
       RelationshipKind.GOVERNS: {
            'valid_combinations': [
                ('Actor', 'Actor'),
                ('Actor', 'Institution'),
                ('Actor', 'Policy'),
                ('Actor', 'Resource'),  # Actors can govern resources (ownership, stewardship)
                ('Institution', 'Institution'),
                ('Institution', 'Actor'),
                ('Institution', 'Policy'),  # Institutions can govern policies
                ('Institution', 'Resource'),  # Institutions can govern/regulate resources
                ('Policy', 'Actor'),
                ('Policy', 'Institution'),
                ('Policy', 'Resource')  # Policies can govern resources (regulations)
            ],
            'description': ('GOVERNS relationship requires entities capable of '
                           'authority or regulation'),
            'invalid_message': ('GOVERNS relationship requires authority-capable '
                               'entities (Actors, Institutions, Policies) '
                               'governing appropriate targets')
        },
        RelationshipKind.EMPLOYS: {
            'valid_combinations': [
                ('Actor', 'Actor'),
                ('Institution', 'Actor')  # Organizations can employ people
            ],
            'description': 'EMPLOYS relationship for labor relationships',
            'invalid_message': ('EMPLOYS relationship requires Actor or Institution '
                               'employing Actor entities')
        },
        RelationshipKind.OWNS: {
            'valid_combinations': [
                ('Actor', 'Resource'),
                ('Institution', 'Resource'),
                ('Actor', 'TechnologySystem'),
                ('Institution', 'TechnologySystem')
            ],
            'description': ('OWNS relationship requires an entity capable of ownership '
                           'and an ownable resource'),
            'invalid_message': ('OWNS relationship requires Actor/Institution '
                               'owning Resource/TechnologySystem')
        },
        RelationshipKind.USES: {
            'valid_combinations': [
                ('Actor', 'Resource'),
                ('Process', 'Resource'),
                ('Actor', 'TechnologySystem'),
                ('Process', 'TechnologySystem'),
                ('Actor', 'Institution'),
                ('Process', 'Institution')
            ],
            'description': 'USES relationship requires a user and a usable entity',
            'invalid_message': ('USES relationship requires Actor/Process using '
                               'Resource/TechnologySystem/Institution')
        },
        RelationshipKind.PRODUCES: {
            'valid_combinations': [
                ('Actor', 'Resource'),
                ('Process', 'Resource'),
                ('TechnologySystem', 'Resource'),
                ('Actor', 'Flow'),
                ('Process', 'Flow'),
                ('TechnologySystem', 'Flow'),
                ('Actor', 'ValueFlow'),
                ('Process', 'ValueFlow'),
                ('TechnologySystem', 'ValueFlow'),
                ('PolicyInstrument', 'Flow'),
                ('PolicyInstrument', 'ValueFlow'),
                ('PolicyInstrument', 'Resource')
            ],
            'description': 'PRODUCES relationship requires a producer and a producible output',
            'invalid_message': ('PRODUCES relationship requires '
                               'Actor/Process/TechnologySystem/PolicyInstrument '
                               'producing Resource/Flow/ValueFlow')
        },
        
        # Enhanced governance relationships
        RelationshipKind.REGULATES: {
            'valid_combinations': [
                ('Actor', 'Actor'),
                ('Institution', 'Actor'),
                ('Policy', 'Actor'),
                ('Actor', 'Institution'),
                ('Institution', 'Institution'),
                ('Policy', 'Institution'),
                ('Actor', 'Resource'),
                ('Institution', 'Resource'),
                ('Policy', 'Resource'),
                ('Actor', 'TechnologySystem'),
                ('Institution', 'TechnologySystem'),
                ('Policy', 'TechnologySystem')
            ],
            'description': 'REGULATES relationship requires regulatory authority',
            'invalid_message': ('REGULATES relationship requires authority entities '
                               '(Actor/Institution/Policy) regulating appropriate targets')
        },
        
        RelationshipKind.INFLUENCES: {
            'valid_combinations': [
                ('Actor', 'Actor'),
                ('Actor', 'Institution'),
                ('Actor', 'Policy'),
                ('Institution', 'Actor'),
                ('Institution', 'Institution'),
                ('Institution', 'Policy'),
                ('Policy', 'Actor'),     # Policies can influence actors
                ('Policy', 'Institution'),  # Policies can influence institutions
                ('Policy', 'Resource'),  # Policies can influence resource management/usage
                ('Resource', 'Actor'),
                ('Resource', 'Institution'),
                ('Flow', 'Actor'),
                ('Flow', 'Institution'),
                ('TechnologySystem', 'Actor'),
                ('TechnologySystem', 'Institution'),
                ('TechnologySystem', 'Policy'),
                ('Actor', 'InstrumentalBehavior'),  # Actors can influence behaviors
                ('Actor', 'CeremonialBehavior'),   # Actors can influence behaviors
                ('Institution', 'InstrumentalBehavior'),  # Institutions can influence behaviors
                ('Institution', 'CeremonialBehavior'),    # Institutions can influence behaviors
                ('PolicyInstrument', 'InstrumentalBehavior'),  # Policy instruments can influence behaviors
                ('PolicyInstrument', 'CeremonialBehavior')     # Policy instruments can influence behaviors
            ],
            'description': 'INFLUENCES relationship for impact and effect patterns',
            'invalid_message': ('INFLUENCES relationship requires influence-capable entities '
                               'affecting decision-makers or systems')
        },
        
        RelationshipKind.FUNDS: {
            'valid_combinations': [
                ('Actor', 'Actor'),
                ('Institution', 'Actor'),
                ('Actor', 'Institution'),
                ('Institution', 'Institution'),
                ('Policy', 'Actor'),        # Policies can establish funding for actors
                ('Policy', 'Institution'),  # Policies can establish funding for institutions
                ('Actor', 'Resource'),
                ('Institution', 'Resource'),
                ('Actor', 'Process'),
                ('Institution', 'Process'),
                ('Actor', 'TechnologySystem'),
                ('Institution', 'TechnologySystem')
            ],
            'description': 'FUNDS relationship for financial resource provision',
            'invalid_message': ('FUNDS relationship requires funding entities '
                               '(Actor/Institution/Policy) providing financial resources')
        },
        
        RelationshipKind.SUPPLIES: {
            'valid_combinations': [
                ('Actor', 'Actor'),
                ('Institution', 'Actor'),
                ('Actor', 'Institution'),
                ('Institution', 'Institution'),
                ('Actor', 'Process'),
                ('Institution', 'Process'),
                ('Resource', 'Actor'),
                ('Resource', 'Institution'),
                ('Resource', 'Process'),
                ('TechnologySystem', 'Actor'),
                ('TechnologySystem', 'Institution'),
                ('TechnologySystem', 'Process')
            ],
            'description': 'SUPPLIES relationship for resource provision',
            'invalid_message': ('SUPPLIES relationship requires suppliers providing '
                               'resources to recipients')
        },
        
        RelationshipKind.IMPLEMENTS: {
            'valid_combinations': [
                ('Actor', 'Policy'),
                ('Institution', 'Policy'),
                ('Actor', 'Institution'),
                ('Institution', 'Institution'),
                ('Process', 'Policy'),
                ('TechnologySystem', 'Policy'),
                ('PolicyInstrument', 'Policy'),
                ('Policy', 'PolicyInstrument')  # Policies implement through policy instruments
            ],
            'description': 'IMPLEMENTS relationship for policy and institutional execution',
            'invalid_message': ('IMPLEMENTS relationship requires implementing entities '
                               'executing policies or institutional arrangements')
        },
        
        RelationshipKind.TRANSFORMS: {
            'valid_combinations': [
                ('Process', 'Resource'),
                ('TechnologySystem', 'Resource'),
                ('PolicyInstrument', 'Resource'),
                ('Process', 'Actor'),
                ('TechnologySystem', 'Actor'),
                ('PolicyInstrument', 'Actor'),
                ('Process', 'Flow'),
                ('TechnologySystem', 'Flow'),
                ('PolicyInstrument', 'Flow'),
                ('Process', 'ValueFlow'),
                ('TechnologySystem', 'ValueFlow'),
                ('PolicyInstrument', 'ValueFlow')
            ],
            'description': 'TRANSFORMS relationship for change and conversion processes',
            'invalid_message': ('TRANSFORMS relationship requires active change agents '
                               '(Process/TechnologySystem/PolicyInstrument) transforming targets')
        },
        
        RelationshipKind.COLLABORATES_WITH: {
            'valid_combinations': [
                ('Actor', 'Actor'),
                ('Institution', 'Institution'),
                ('Actor', 'Institution'),
                ('Institution', 'Actor'),
                ('Process', 'Process'),
                ('Actor', 'Process'),
                ('Institution', 'Process')
            ],
            'description': 'COLLABORATES_WITH relationship for cooperative arrangements',
            'invalid_message': ('COLLABORATES_WITH relationship requires cooperative entities '
                               'working together')
        },
        
        RelationshipKind.COORDINATES_WITH: {
            'valid_combinations': [
                ('Actor', 'Actor'),
                ('Institution', 'Institution'),
                ('Actor', 'Institution'),
                ('Institution', 'Actor'),
                ('Process', 'Process'),
                ('Actor', 'Process'),
                ('Institution', 'Process'),
                ('TechnologySystem', 'TechnologySystem'),
                ('TechnologySystem', 'Process')
            ],
            'description': 'COORDINATES_WITH relationship for alignment and synchronization',
            'invalid_message': ('COORDINATES_WITH relationship requires coordinating entities '
                               'aligning activities')
        }
    }

    @staticmethod
    def validate_relationship_context(
        kind: RelationshipKind,
        source_type: str,
        target_type: str
    ) -> None:
        """Validate that relationship makes sense in context.

        Args:
            kind: The type of relationship
            source_type: Type of source node (class name)
            target_type: Type of target node (class name)

        Raises:
            IncompatibleEnumError: If relationship doesn't make sense
            InvalidEnumOperationError: If invalid parameters provided
        """

        if not source_type or not target_type:
            raise InvalidEnumOperationError(
                "Source and target types must be provided and non-empty"
            )

        # Check if we have specific rules for this relationship kind
        if kind in EnumValidator.RELATIONSHIP_RULES:
            rule = EnumValidator.RELATIONSHIP_RULES[kind]
            valid_combinations = rule['valid_combinations']
            
            if isinstance(valid_combinations, str) or (source_type, target_type) not in valid_combinations:
                suggestions = EnumValidator._generate_suggestions(kind, source_type, target_type)
                raise IncompatibleEnumError(
                    f"{rule['invalid_message']}. "
                    f"Got {source_type}->{target_type}. "
                    f"{suggestions}"
                )

    @staticmethod
    def validate_flow_combination(nature: FlowNature, flow_type: FlowType) -> None:
        """Validate that flow nature and type are compatible.

        Args:
            nature: The nature of the flow
            flow_type: The type of the flow

        Raises:
            IncompatibleEnumError: If flow nature and type are incompatible
            InvalidEnumOperationError: If invalid parameters provided
        """

        # Define obviously incompatible combinations (semantically impossible)
        strictly_incompatible = {
            # These combinations are clearly nonsensical
            (FlowNature.ENERGY, FlowType.INFORMATION),
            (FlowNature.INFORMATION, FlowType.ENERGY),
            # Physical flows cannot be purely informational
            (FlowNature.MATERIAL, FlowType.INFORMATION),
            (FlowNature.MATERIAL, FlowType.SOCIAL),
            # Financial flows cannot be material or energy
            (FlowNature.FINANCIAL, FlowType.MATERIAL),
            (FlowNature.FINANCIAL, FlowType.ENERGY),
            # Information flows cannot be material or energy
            (FlowNature.INFORMATION, FlowType.MATERIAL),
            # Energy flows cannot be informational or social
            (FlowNature.ENERGY, FlowType.SOCIAL),
            # Social flows are not material or energy based
            (FlowNature.SOCIAL, FlowType.MATERIAL),
            (FlowNature.SOCIAL, FlowType.ENERGY),
            # Service flows are not typically material
            (FlowNature.SERVICE, FlowType.MATERIAL),
            (FlowNature.SERVICE, FlowType.ENERGY),
            # Cultural flows are not material or energy based
            (FlowNature.CULTURAL, FlowType.MATERIAL),
            (FlowNature.CULTURAL, FlowType.ENERGY),
            # Regulatory flows are primarily informational
            (FlowNature.REGULATORY, FlowType.MATERIAL),
            (FlowNature.REGULATORY, FlowType.ENERGY),
        }

        if (nature, flow_type) in strictly_incompatible:
            raise IncompatibleEnumError(
                f"Flow nature {nature.name} is semantically incompatible with "
                f"flow type {flow_type.name}. Consider using compatible combinations."
            )

    @staticmethod
    def validate_institution_layer_context(
        layer: InstitutionLayer,
        institution_type: str
    ) -> None:
        """Validate that institution layer makes sense for the institution type.

        Args:
            layer: The institutional layer
            institution_type: Type of institution

        Raises:
            IncompatibleEnumError: If layer doesn't match institution type
            InvalidEnumOperationError: If invalid parameters provided
        """

        # Formal rules should typically apply to formal institutions
        if (layer == InstitutionLayer.FORMAL_RULE and
            institution_type in ['BeliefSystem', 'ValueSystem']):
            raise IncompatibleEnumError(
                f"FORMAL_RULE layer is typically not appropriate for {institution_type}. "
                f"Consider using CULTURAL_VALUE or KNOWLEDGE_SYSTEM layers for "
                f"belief/value systems."
            )

    @staticmethod
    def validate_policy_instrument_combination(
        instrument_type: PolicyInstrumentType,
        target_context: str
    ) -> None:
        """Validate that policy instrument type is appropriate for target context.

        Args:
            instrument_type: The type of policy instrument
            target_context: Context where the instrument is being applied

        Raises:
            IncompatibleEnumError: If instrument type doesn't match context
            InvalidEnumOperationError: If invalid parameters provided
        """
        if not target_context:
            raise InvalidEnumOperationError(
                "Target context must be provided and non-empty"
            )

        # Define inappropriate combinations
        inappropriate_combinations = {
            # Regulatory instruments should not be used for voluntary contexts
            (PolicyInstrumentType.REGULATORY, 'voluntary'),
            (PolicyInstrumentType.REGULATORY, 'market_based'),
            # Economic instruments less effective for information provision
            (PolicyInstrumentType.ECONOMIC, 'information_provision'),
            (PolicyInstrumentType.ECONOMIC, 'awareness_building'),
        }

        if (instrument_type, target_context.lower()) in inappropriate_combinations:
            raise IncompatibleEnumError(
                f"Policy instrument {instrument_type.name} may not be appropriate for "
                f"{target_context} context. Consider alternative instrument types that "
                f"better align with the target context."
            )

    @staticmethod
    def validate_value_category_context(
        category: ValueCategory,
        measurement_context: str
    ) -> None:
        """Validate that value category is appropriate for measurement context.

        Args:
            category: The value category being measured
            measurement_context: Context of measurement (e.g., 'quantitative', 'qualitative')

        Raises:
            IncompatibleEnumError: If category doesn't match measurement context
            InvalidEnumOperationError: If invalid parameters provided
        """

        if not measurement_context:
            raise InvalidEnumOperationError(
                "Measurement context must be provided and non-empty"
            )

        # Define categories that are difficult to measure quantitatively
        qualitative_preferred = {
            ValueCategory.CULTURAL, ValueCategory.SPIRITUAL, ValueCategory.AESTHETIC,
            ValueCategory.ETHICAL, ValueCategory.PSYCHOLOGICAL, ValueCategory.COMMUNITY
        }

        # Define categories that are typically quantitative
        quantitative_preferred = {
            ValueCategory.ECONOMIC, ValueCategory.PERFORMANCE, ValueCategory.EFFICIENCY,
            ValueCategory.EFFECTIVENESS, ValueCategory.DEMOGRAPHIC
        }

        context_lower = measurement_context.lower()

        if (context_lower == 'quantitative' and category in qualitative_preferred):
            raise IncompatibleEnumError(
                f"Value category {category.name} is typically difficult to measure "
                f"quantitatively. Consider qualitative measurement approaches or "
                f"complementary quantitative indicators."
            )

        if (context_lower == 'qualitative' and category in quantitative_preferred):
            raise IncompatibleEnumError(
                f"Value category {category.name} is typically measured quantitatively. "
                f"Consider quantitative measurement approaches or mixed-method evaluation."
            )

    @staticmethod
    def validate_cross_enum_dependency(
        primary_enum: Enum,
        dependent_enum: Enum,
        relationship_type: str
    ) -> None:
        """Validate cross-enum dependencies and relationships.

        Args:
            primary_enum: The primary enum that constrains choices
            dependent_enum: The dependent enum that must align with primary
            relationship_type: Type of dependency relationship

        Raises:
            IncompatibleEnumError: If enums are incompatible
            InvalidEnumOperationError: If invalid parameters provided
        """
        if not relationship_type:
            raise InvalidEnumOperationError(
                "Relationship type must be provided and non-empty"
            )

        # Handle flow nature and institution layer dependencies
        if (isinstance(primary_enum, FlowNature) and
            isinstance(dependent_enum, InstitutionLayer) and
            relationship_type.lower() == 'governance'):

            # Financial flows should typically be governed by formal institutions
            if (primary_enum == FlowNature.FINANCIAL and
                dependent_enum == InstitutionLayer.INFORMAL_NORM):
                raise IncompatibleEnumError(
                    f"Financial flows ({primary_enum.name}) typically require formal institutional governance, "
                    f"not {dependent_enum.name}. Consider FORMAL_RULE or ORGANIZATION layers."
                )

            # Cultural flows align better with cultural value layers
            if (primary_enum == FlowNature.CULTURAL and
                dependent_enum == InstitutionLayer.FORMAL_RULE):
                raise IncompatibleEnumError(
                    f"Cultural flows ({primary_enum.name}) may be over-regulated by {dependent_enum.name}. "
                    f"Consider CULTURAL_VALUE or INFORMAL_NORM layers."
                )

    @staticmethod
    def validate_required_enum_context(
        enum_value: Enum,
        context: str,
        is_required: bool = True
    ) -> None:
        """Validate whether an enum is required or optional in given context.

        Args:
            enum_value: The enum value to validate
            context: The context where the enum is used
            is_required: Whether the enum is required in this context

        Raises:
            InvalidEnumOperationError: If required enum is missing or invalid
        """
        if not context:
            raise InvalidEnumOperationError(
                "Context must be provided and non-empty"
            )

        # Define contexts where specific enums are required
        required_contexts: Dict[str, List[Type[Enum]]] = {
            'financial_transaction': [FlowNature, FlowType],
            'policy_implementation': [PolicyInstrumentType],
            'institutional_analysis': [InstitutionLayer],
            'value_measurement': [ValueCategory],
            'relationship_creation': [RelationshipKind]
        }

        context_lower = context.lower()
        if context_lower in required_contexts:
            required_enum_types = required_contexts[context_lower]
            enum_type = type(enum_value)

            if is_required and enum_type not in required_enum_types:
                raise InvalidEnumOperationError(
                    f"Context '{context}' requires one of these enum types: "
                    f"{[t.__name__ for t in required_enum_types]}, but got {enum_type.__name__}"
                )

            if not is_required and enum_type in required_enum_types:
                # This is fine - optional usage of a typically required enum
                pass

    @staticmethod
    def validate_technology_readiness_level(
        level: TechnologyReadinessLevel,
        context: str = "general"
    ) -> None:
        """Validate TechnologyReadinessLevel usage in context.

        Args:
            level: The TRL level to validate
            context: Context where TRL is being used

        Raises:
            InvalidEnumOperationError: If invalid parameters provided
            IncompatibleEnumError: If TRL inappropriate for context
        """
        if not context:
            raise InvalidEnumOperationError(
                "Context must be provided and non-empty"
            )

        # Define context-specific validation rules
        context_lower = context.lower()

        # Research contexts typically use lower TRL levels
        if context_lower in ['research', 'basic_research', 'laboratory']:
            if level.value > 6:
                raise IncompatibleEnumError(
                    f"TRL {level.value} ({level.name}) may be too advanced for {context} context. "
                    f"Research contexts typically use TRL 1-6."
                )

        # Commercial contexts typically require higher TRL levels
        elif context_lower in ['commercial', 'production', 'deployment']:
            if level.value < 7:
                raise IncompatibleEnumError(
                    f"TRL {level.value} ({level.name}) may be too early for {context} context. "
                    f"Commercial contexts typically require TRL 7-9."
                )

    @staticmethod
    def validate_legitimacy_source_context(
        source: LegitimacySource,
        institutional_context: str
    ) -> None:
        """Validate LegitimacySource appropriateness for institutional context.

        Args:
            source: The legitimacy source to validate
            institutional_context: Type of institutional context

        Raises:
            InvalidEnumOperationError: If invalid parameters provided
            IncompatibleEnumError: If source inappropriate for context
        """
        if not institutional_context:
            raise InvalidEnumOperationError(
                "Institutional context must be provided and non-empty"
            )

        context_lower = institutional_context.lower()

        # Traditional legitimacy rarely appropriate for modern bureaucratic contexts
        if source == LegitimacySource.TRADITIONAL and context_lower in [
            'bureaucracy', 'modern_government', 'corporation', 'scientific_institution'
        ]:
            raise IncompatibleEnumError(
                f"Traditional legitimacy may not be appropriate for "
                f"{institutional_context}. Consider LEGAL_RATIONAL or EXPERT "
                f"legitimacy sources."
            )

        # Charismatic legitimacy typically unstable for large-scale institutions
        if source == LegitimacySource.CHARISMATIC and context_lower in [
            'large_organization', 'government_agency', 'public_administration'
        ]:
            raise IncompatibleEnumError(
                f"Charismatic legitimacy may be inappropriate for "
                f"{institutional_context}. Large-scale institutions typically "
                f"require LEGAL_RATIONAL legitimacy."
            )

        # Expert legitimacy most appropriate for technical/scientific contexts
        if source != LegitimacySource.EXPERT and context_lower in [
            'technical_organization', 'research_institution', 'professional_body'
        ]:
            # This is a warning rather than error - other sources can exist
            # but expert is preferred
            pass

    @staticmethod
    def _generate_suggestions(kind: RelationshipKind, source_type: str, target_type: str) -> str:
        """Generate intelligent, context-aware suggestions for valid combinations.
        
        Enhanced suggestion algorithm that provides:
        - Semantic analysis of relationship types
        - Entity type compatibility assessment
        - Context-aware alternative recommendations
        - SFM-specific business logic guidance
        """
        suggestions: List[str] = []
        
        # Try specific rules first for basic suggestions
        if kind in EnumValidator.RELATIONSHIP_RULES:
            valid_combinations = EnumValidator.RELATIONSHIP_RULES[kind]['valid_combinations']

            # Find suggestions for the source type
            source_suggestions = [combo[1] for combo in valid_combinations if combo[0] == source_type]
            target_suggestions = [combo[0] for combo in valid_combinations if combo[1] == target_type]

            if source_suggestions:
                suggestions.append(f"For {source_type} sources, valid targets are: {', '.join(set(source_suggestions))}")
            if target_suggestions:
                suggestions.append(f"For {target_type} targets, valid sources are: {', '.join(set(target_suggestions))}")
        
        # Always enhance with intelligent suggestion algorithms
        semantic_suggestions = EnumValidator._generate_semantic_suggestions(kind, source_type, target_type)
        if semantic_suggestions:
            suggestions.extend(semantic_suggestions)
        
        # Business logic suggestions based on SFM principles
        business_suggestions = EnumValidator._generate_business_logic_suggestions(kind, source_type, target_type)
        if business_suggestions:
            suggestions.extend(business_suggestions)
        
        # Context-aware entity compatibility suggestions
        entity_suggestions = EnumValidator._generate_entity_compatibility_suggestions(source_type, target_type)
        if entity_suggestions:
            suggestions.extend(entity_suggestions)
        
        if suggestions:
            return "Suggestions: " + "; ".join(suggestions)
        
        return "Check the relationship documentation for valid combinations."

    @staticmethod 
    def _generate_semantic_suggestions(kind: RelationshipKind, source_type: str, target_type: str) -> List[str]:
        """Generate suggestions based on semantic analysis of relationship types."""
        suggestions = []
        
        # Categorize relationships by semantic meaning
        governance_relations = {
            RelationshipKind.GOVERNS, RelationshipKind.REGULATES, RelationshipKind.MANDATES,
            RelationshipKind.AUTHORIZES, RelationshipKind.ENFORCES, RelationshipKind.DELEGATES,
            RelationshipKind.LICENSES, RelationshipKind.CERTIFIES, RelationshipKind.SANCTIONS
        }
        
        resource_flow_relations = {
            RelationshipKind.FUNDS, RelationshipKind.PAYS, RelationshipKind.ALLOCATES,
            RelationshipKind.TRANSFERS, RelationshipKind.SUPPLIES, RelationshipKind.PRODUCES,
            RelationshipKind.DISTRIBUTES, RelationshipKind.CONVERTS, RelationshipKind.EXCHANGES_WITH
        }
        
        knowledge_relations = {
            RelationshipKind.INFORMS, RelationshipKind.EDUCATES, RelationshipKind.ADVISES,
            RelationshipKind.RESEARCHES, RelationshipKind.ANALYZES, RelationshipKind.COMMUNICATES_WITH,
            RelationshipKind.DOCUMENTS, RelationshipKind.MEASURES
        }
        
        collaborative_relations = {
            RelationshipKind.COLLABORATES_WITH, RelationshipKind.COORDINATES_WITH,
            RelationshipKind.SUPPORTS, RelationshipKind.ALLIES_WITH, RelationshipKind.FACILITATES,
            RelationshipKind.PARTICIPATES_IN, RelationshipKind.ORGANIZES
        }
        
        # Provide semantic category guidance
        if kind in governance_relations:
            if source_type not in ['Actor', 'Institution', 'Policy']:
                suggestions.append(f"Governance relationships like {kind.name} typically require Actor, Institution, or Policy as source")
            if target_type in ['Actor', 'Institution', 'Policy', 'Resource']:
                suggestions.append(f"Consider {kind.name} with governable entities: Actor, Institution, Policy, or Resource")
                
        elif kind in resource_flow_relations:
            if source_type not in ['Actor', 'Institution', 'Process', 'PolicyInstrument']:
                suggestions.append(f"Resource flow relationships like {kind.name} typically require entities capable of resource handling")
            if target_type not in ['Actor', 'Resource', 'Flow', 'ValueFlow']:
                suggestions.append(f"Consider {kind.name} targeting resource-receiving entities: Actor, Resource, Flow, or ValueFlow")
                
        elif kind in knowledge_relations:
            if source_type not in ['Actor', 'Institution', 'TechnologySystem']:
                suggestions.append(f"Knowledge relationships like {kind.name} typically require information-capable entities")
            if target_type not in ['Actor', 'Institution', 'Resource', 'TechnologySystem']:
                suggestions.append(f"Consider {kind.name} with information-receiving entities")
                
        elif kind in collaborative_relations:
            if source_type not in ['Actor', 'Institution']:
                suggestions.append(f"Collaborative relationships like {kind.name} typically require social entities like Actor or Institution")
            if target_type not in ['Actor', 'Institution', 'Process']:
                suggestions.append(f"Consider {kind.name} with collaborative entities: Actor, Institution, or Process")
        
        return suggestions

    @staticmethod
    def _generate_business_logic_suggestions(kind: RelationshipKind, source_type: str, target_type: str) -> List[str]:
        """Generate suggestions based on SFM business logic and domain constraints."""
        suggestions = []
        
        # SFM-specific institutional analysis patterns
        if kind == RelationshipKind.IMPLEMENTS and source_type == 'Actor':
            if target_type not in ['Policy', 'Institution']:
                suggestions.append("Actors typically implement Policies or institutional arrangements")
                
        elif kind == RelationshipKind.INFLUENCES:
            if source_type in ['Resource', 'Flow'] and target_type in ['Actor', 'Institution']:
                suggestions.append("Resources and Flows can influence decision-making entities")
            elif source_type in ['Actor', 'Institution'] and target_type in ['Actor', 'Institution', 'Policy']:
                suggestions.append("Social entities can influence other social entities and policies")
                
        elif kind == RelationshipKind.TRANSFORMS:
            if source_type not in ['Process', 'TechnologySystem', 'PolicyInstrument']:
                suggestions.append("Transformation typically requires active change agents: Process, TechnologySystem, or PolicyInstrument")
            if target_type not in ['Resource', 'Flow', 'ValueFlow', 'Actor']:
                suggestions.append("Consider transformation targets: Resource, Flow, ValueFlow, or Actor")
                
        # Hayden's institutional layer compatibility
        elif kind in [RelationshipKind.ENFORCES, RelationshipKind.SANCTIONS]:
            if source_type != 'Institution':
                suggestions.append("Enforcement and sanctions typically come from institutional authority")
                
        # Economic flow patterns
        elif kind in [RelationshipKind.BUYS_FROM, RelationshipKind.SELLS_TO, RelationshipKind.PAYS]:
            if source_type not in ['Actor', 'Institution']:
                suggestions.append("Economic transactions require economic actors")
            if target_type not in ['Actor', 'Institution']:
                suggestions.append("Economic transactions target other economic actors")
        
        return suggestions

    @staticmethod 
    def _generate_entity_compatibility_suggestions(source_type: str, target_type: str) -> List[str]:
        """Generate suggestions based on entity type compatibility in SFM framework."""
        suggestions = []
        
        # Get entity type categories for analysis
        source_category = EnumValidator._get_entity_category(source_type)
        target_category = EnumValidator._get_entity_category(target_type)
        
        # Suggest compatible entity combinations
        if source_category == 'social' and target_category == 'structural':
            suggestions.append("Social entities (Actor, Institution) work well with structural entities (Resource, TechnologySystem)")
            
        elif source_category == 'active' and target_category == 'passive':
            suggestions.append("Active entities (Actor, Process) can effectively operate on passive entities (Resource, Flow)")
            
        elif source_category == 'authority' and target_category in ['social', 'structural']:
            suggestions.append("Authority entities (Institution, Policy) can govern social and structural entities")
            
        elif source_type == target_type:
            suggestions.append(f"Same-type relationships ({source_type}->{target_type}) may indicate peer interaction patterns")
        
        return suggestions

    @staticmethod
    def _get_entity_category(entity_type: str) -> str:
        """Categorize entity types for compatibility analysis."""
        if entity_type in EnumValidator.ACTOR_TYPES:
            return 'social'
        elif entity_type in EnumValidator.INSTITUTION_TYPES:
            return 'authority'
        elif entity_type in EnumValidator.RESOURCE_TYPES:
            return 'structural'
        elif entity_type in EnumValidator.PROCESS_TYPES:
            return 'active'
        elif entity_type in EnumValidator.SYSTEM_TYPES:
            return 'structural'
        else:
            return 'other'

    @staticmethod
    def validate_cross_entity_consistency(
        entity_1_type: str, 
        entity_2_type: str, 
        relationship_kind: RelationshipKind,
        context: str = "general"
    ) -> None:
        """Validate consistency across multiple entities in SFM framework.
        
        This method implements advanced cross-entity validation rules that ensure
        entities work together coherently within the SFM framework, considering
        business logic and domain constraints.
        
        Args:
            entity_1_type: Type of first entity
            entity_2_type: Type of second entity  
            relationship_kind: The relationship connecting them
            context: Additional context for validation
            
        Raises:
            IncompatibleEnumError: If entities are inconsistent
            InvalidEnumOperationError: If invalid parameters provided
        """
        if not entity_1_type or not entity_2_type:
            raise InvalidEnumOperationError(
                "Entity types must be provided and non-empty"
            )
        
        # Basic relationship validation first
        EnumValidator.validate_relationship_context(relationship_kind, entity_1_type, entity_2_type)
        
        # Advanced consistency checks based on SFM principles
        
        # Authority consistency: governance relationships require clear authority hierarchy
        governance_relationships = {
            RelationshipKind.GOVERNS, RelationshipKind.REGULATES, RelationshipKind.MANDATES,
            RelationshipKind.AUTHORIZES, RelationshipKind.ENFORCES
        }
        
        if relationship_kind in governance_relationships:
            if entity_1_type in ['Resource', 'Flow'] and entity_2_type in ['Actor', 'Institution']:
                raise IncompatibleEnumError(
                    f"Authority inconsistency: {entity_1_type} cannot exercise governance "
                    f"over {entity_2_type}. Governance requires authority-capable entities."
                )
        
        # Economic consistency: financial relationships require economic capability
        economic_relationships = {
            RelationshipKind.FUNDS, RelationshipKind.PAYS, RelationshipKind.BUYS_FROM,
            RelationshipKind.SELLS_TO, RelationshipKind.INVESTS_IN
        }
        
        if relationship_kind in economic_relationships:
            non_economic_entities = ['Flow', 'ValueFlow', 'Process']
            if entity_1_type in non_economic_entities or entity_2_type in non_economic_entities:
                raise IncompatibleEnumError(
                    f"Economic inconsistency: {relationship_kind.name} relationship "
                    f"between {entity_1_type} and {entity_2_type} requires economic actors. "
                    f"Consider Actor or Institution entities for economic transactions."
                )
        
        # Temporal consistency: ensure entity lifecycles are compatible
        if context.lower() in ['temporal', 'time_series']:
            temporal_sensitive = {
                RelationshipKind.PRECEDES, RelationshipKind.FOLLOWS, RelationshipKind.TRIGGERS,
                RelationshipKind.SYNCHRONIZES_WITH, RelationshipKind.SUPERSEDES
            }
            
            if relationship_kind in temporal_sensitive:
                # Structural entities (Resources, Systems) may have different temporal patterns
                if entity_1_type in ['Resource', 'TechnologySystem'] and entity_2_type in ['Actor']:
                    # This is acceptable but requires careful temporal modeling
                    pass
        
        # Spatial consistency: ensure entities can interact spatially
        if context.lower() in ['spatial', 'geographic']:
            spatial_relationships = {
                RelationshipKind.LOCATED_IN, RelationshipKind.CONNECTS, RelationshipKind.TRANSPORTS,
                RelationshipKind.CONTAINS, RelationshipKind.ENCOMPASSES
            }
            
            if relationship_kind in spatial_relationships:
                if entity_1_type in ['Flow', 'ValueFlow'] and entity_2_type in ['Flow', 'ValueFlow']:
                    raise IncompatibleEnumError(
                        f"Spatial inconsistency: {relationship_kind.name} between flows "
                        f"may require spatial anchor entities (Actor, Institution, Resource)."
                    )

    @staticmethod
    def validate_business_rule_constraints(
        relationship_kind: RelationshipKind,
        source_type: str,
        target_type: str,
        domain_context: str = "general"
    ) -> None:
        """Validate SFM-specific business rules and domain constraints.
        
        This method implements domain-specific validation rules based on Hayden's
        institutional analysis framework and SFM methodology.
        
        Args:
            relationship_kind: The relationship type to validate
            source_type: Source entity type
            target_type: Target entity type
            domain_context: Domain-specific context (e.g., 'environmental', 'economic')
            
        Raises:
            IncompatibleEnumError: If business rules are violated
            InvalidEnumOperationError: If invalid parameters provided
        """
        if not all([relationship_kind, source_type, target_type]):
            raise InvalidEnumOperationError(
                "All parameters must be provided and non-empty"
            )
        
        domain_lower = domain_context.lower()
        
        # Environmental domain constraints
        if domain_lower in ['environmental', 'sustainability', 'ecological']:
            # Environmental policies should primarily regulate actors and resources
            if relationship_kind == RelationshipKind.REGULATES and source_type == 'Policy':
                if target_type not in ['Actor', 'Resource', 'TechnologySystem']:
                    raise IncompatibleEnumError(
                        f"Environmental regulatory constraint: Policy should regulate "
                        f"entities with environmental impact (Actor/Resource/TechnologySystem), "
                        f"not {target_type}."
                    )
            
            # Environmental flows should connect to resource or actor entities
            if relationship_kind in [RelationshipKind.PRODUCES, RelationshipKind.CONSUMES]:
                if source_type == 'Flow' and target_type not in ['Resource', 'Actor']:
                    raise IncompatibleEnumError(
                        f"Environmental flow constraint: {relationship_kind.name} from Flow "
                        f"should target Resource or Actor entities in environmental context."
                    )
        
        # Economic domain constraints
        elif domain_lower in ['economic', 'financial', 'market']:
            # Market relationships require economic actors
            market_relationships = {
                RelationshipKind.COMPETES_WITH, RelationshipKind.BUYS_FROM, 
                RelationshipKind.SELLS_TO, RelationshipKind.CONTRACTS_WITH
            }
            
            if relationship_kind in market_relationships:
                if source_type not in ['Actor', 'Institution'] or target_type not in ['Actor', 'Institution']:
                    raise IncompatibleEnumError(
                        f"Economic constraint: Market relationship {relationship_kind.name} "
                        f"requires economic actors (Actor/Institution), got {source_type}->{target_type}."
                    )
            
            # Investment relationships require financial capability
            if relationship_kind == RelationshipKind.INVESTS_IN:
                if source_type not in ['Actor', 'Institution']:
                    raise IncompatibleEnumError(
                        f"Economic constraint: Investment requires Actor or Institution "
                        f"as investor, not {source_type}."
                    )
        
        # Social domain constraints  
        elif domain_lower in ['social', 'community', 'governance']:
            # Social coordination requires social entities
            social_relationships = {
                RelationshipKind.COLLABORATES_WITH, RelationshipKind.COORDINATES_WITH,
                RelationshipKind.PARTICIPATES_IN, RelationshipKind.ORGANIZES
            }
            
            if relationship_kind in social_relationships:
                if source_type not in ['Actor', 'Institution']:
                    raise IncompatibleEnumError(
                        f"Social constraint: {relationship_kind.name} requires social entities "
                        f"(Actor/Institution) as participants, not {source_type}."
                    )
        
        # Institutional domain constraints (Hayden's framework)
        elif domain_lower in ['institutional', 'policy', 'governance']:
            # Institutional implementation requires clear authority
            if relationship_kind == RelationshipKind.IMPLEMENTS:
                if source_type not in ['Actor', 'Institution', 'PolicyInstrument']:
                    raise IncompatibleEnumError(
                        f"Institutional constraint: Policy implementation requires "
                        f"implementing entities (Actor/Institution/PolicyInstrument), not {source_type}."
                    )
                
                if target_type not in ['Policy', 'Institution']:
                    raise IncompatibleEnumError(
                        f"Institutional constraint: Implementation should target "
                        f"institutional arrangements (Policy/Institution), not {target_type}."
                    )


def validate_enum_operation(operation_name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator to validate enum operations and provide better error messages.

    Args:
        operation_name: Name of the operation being performed

    Returns:
        Decorator function
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except (TypeError, ValueError, AttributeError) as e:
                raise InvalidEnumOperationError(
                    f"Invalid {operation_name} operation: {str(e)}"
                ) from e
        return wrapper
    return decorator
