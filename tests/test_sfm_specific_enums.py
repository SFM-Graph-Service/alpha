"""
Test module for SFM-specific enums: TechnologyReadinessLevel and LegitimacySource.

This module tests the new enums added to address Issue #28: Missing SFM-Specific Enums.
"""

import unittest
from models.sfm_enums import TechnologyReadinessLevel, LegitimacySource
from models import TechnologySystem, ValueSystem
from data.repositories import SFMRepositoryFactory


class TestTechnologyReadinessLevel(unittest.TestCase):
    """Test TechnologyReadinessLevel enum."""

    def test_enum_values(self):
        """Test that TRL enum has correct values 1-9."""
        self.assertEqual(TechnologyReadinessLevel.BASIC_PRINCIPLES.value, 1)
        self.assertEqual(TechnologyReadinessLevel.TECHNOLOGY_CONCEPT.value, 2)
        self.assertEqual(TechnologyReadinessLevel.EXPERIMENTAL_PROOF.value, 3)
        self.assertEqual(TechnologyReadinessLevel.LABORATORY_VALIDATION.value, 4)
        self.assertEqual(TechnologyReadinessLevel.RELEVANT_ENVIRONMENT.value, 5)
        self.assertEqual(TechnologyReadinessLevel.DEMONSTRATION.value, 6)
        self.assertEqual(TechnologyReadinessLevel.PROTOTYPE_DEMONSTRATION.value, 7)
        self.assertEqual(TechnologyReadinessLevel.SYSTEM_COMPLETE.value, 8)
        self.assertEqual(TechnologyReadinessLevel.ACTUAL_SYSTEM.value, 9)

    def test_enum_completeness(self):
        """Test that all TRL levels 1-9 are represented."""
        values = {level.value for level in TechnologyReadinessLevel}
        expected_values = set(range(1, 10))
        self.assertEqual(values, expected_values)

    def test_technology_system_integration(self):
        """Test TechnologySystem uses TRL enum correctly."""
        tech_sys = TechnologySystem(
            label="Test Technology",
            maturity=TechnologyReadinessLevel.PROTOTYPE_DEMONSTRATION
        )
        
        self.assertIsInstance(tech_sys.maturity, TechnologyReadinessLevel)
        self.assertEqual(tech_sys.maturity.value, 7)
        self.assertEqual(tech_sys.maturity.name, "PROTOTYPE_DEMONSTRATION")

    def test_repository_maturity_range(self):
        """Test that repository maturity range works with enum."""
        repo = SFMRepositoryFactory.create_technology_system_repository()
        
        # Create systems with different maturity levels
        early_tech = TechnologySystem(
            label="Early Tech",
            maturity=TechnologyReadinessLevel.BASIC_PRINCIPLES
        )
        
        mature_tech = TechnologySystem(
            label="Mature Tech", 
            maturity=TechnologyReadinessLevel.PROTOTYPE_DEMONSTRATION
        )
        
        ready_tech = TechnologySystem(
            label="Ready Tech",
            maturity=TechnologyReadinessLevel.ACTUAL_SYSTEM
        )
        
        repo.create(early_tech)
        repo.create(mature_tech)
        repo.create(ready_tech)
        
        # Test range queries
        early_systems = repo.find_by_maturity_range(1, 3)
        self.assertEqual(len(early_systems), 1)
        self.assertEqual(early_systems[0].label, "Early Tech")
        
        mature_systems = repo.find_by_maturity_range(7, 9)
        self.assertEqual(len(mature_systems), 2)
        system_labels = {sys.label for sys in mature_systems}
        self.assertEqual(system_labels, {"Mature Tech", "Ready Tech"})


class TestLegitimacySource(unittest.TestCase):
    """Test LegitimacySource enum."""

    def test_weber_authority_types(self):
        """Test that Weber's three pure types are included."""
        self.assertIn(LegitimacySource.TRADITIONAL, LegitimacySource)
        self.assertIn(LegitimacySource.CHARISMATIC, LegitimacySource)
        self.assertIn(LegitimacySource.LEGAL_RATIONAL, LegitimacySource)

    def test_extended_legitimacy_sources(self):
        """Test that extended legitimacy sources are included."""
        self.assertIn(LegitimacySource.EXPERT, LegitimacySource)
        self.assertIn(LegitimacySource.DEMOCRATIC, LegitimacySource)

    def test_enum_count(self):
        """Test that we have the expected number of legitimacy sources."""
        # Should have 5 sources: Traditional, Charismatic, Legal-Rational, Expert, Democratic
        self.assertEqual(len(list(LegitimacySource)), 5)

    def test_value_system_integration(self):
        """Test ValueSystem uses LegitimacySource enum correctly."""
        value_sys = ValueSystem(
            label="Democratic Values",
            legitimacy_source=LegitimacySource.DEMOCRATIC
        )
        
        self.assertIsInstance(value_sys.legitimacy_source, LegitimacySource)
        self.assertEqual(value_sys.legitimacy_source, LegitimacySource.DEMOCRATIC)

    def test_all_legitimacy_sources_with_value_system(self):
        """Test that all legitimacy sources work with ValueSystem."""
        for source in LegitimacySource:
            value_sys = ValueSystem(
                label=f"Value System - {source.name}",
                legitimacy_source=source
            )
            self.assertEqual(value_sys.legitimacy_source, source)


class TestSFMEnumDocumentation(unittest.TestCase):
    """Test that new enums have proper documentation."""

    def test_technology_readiness_level_docstring(self):
        """Test TRL enum has comprehensive docstring."""
        docstring = TechnologyReadinessLevel.__doc__
        self.assertIsNotNone(docstring)
        self.assertIn("NASA", docstring)
        self.assertIn("Social Fabric Matrix", docstring)
        self.assertIn("Hayden", docstring)

    def test_legitimacy_source_docstring(self):
        """Test LegitimacySource enum has comprehensive docstring."""
        docstring = LegitimacySource.__doc__
        self.assertIsNotNone(docstring)
        self.assertIn("Weber", docstring)
        self.assertIn("authority", docstring)
        self.assertIn("Social Fabric Matrix", docstring)


class TestEnumCompatibility(unittest.TestCase):
    """Test compatibility with existing SFM framework."""

    def test_path_dependency_type_exists(self):
        """Test that PathDependencyType enum already exists (from existing code)."""
        from models.sfm_enums import PathDependencyType
        
        # Should have the expected values
        self.assertIn(PathDependencyType.WEAK, PathDependencyType)
        self.assertIn(PathDependencyType.MODERATE, PathDependencyType)
        self.assertIn(PathDependencyType.STRONG, PathDependencyType)
        self.assertIn(PathDependencyType.LOCKED_IN, PathDependencyType)

    def test_institutional_change_type_exists(self):
        """Test that InstitutionalChangeType enum already exists (from existing code)."""
        from models.sfm_enums import InstitutionalChangeType
        
        # Should have various change mechanisms
        self.assertIn(InstitutionalChangeType.INCREMENTAL, InstitutionalChangeType)
        self.assertIn(InstitutionalChangeType.TRANSFORMATIONAL, InstitutionalChangeType)
        self.assertIn(InstitutionalChangeType.REVOLUTIONARY, InstitutionalChangeType)
        self.assertIn(InstitutionalChangeType.EVOLUTIONARY, InstitutionalChangeType)


class TestSFMSpecificEnumValidation(unittest.TestCase):
    """Test validation for new SFM-specific enums."""

    def test_trl_validation_research_context(self):
        """Test TRL validation in research contexts."""
        from models.sfm_enums import EnumValidator
        
        # Research contexts should accept early TRL levels
        EnumValidator.validate_technology_readiness_level(
            TechnologyReadinessLevel.BASIC_PRINCIPLES, 'research'
        )
        EnumValidator.validate_technology_readiness_level(
            TechnologyReadinessLevel.EXPERIMENTAL_PROOF, 'laboratory'
        )

    def test_trl_validation_commercial_context(self):
        """Test TRL validation in commercial contexts."""
        from models.sfm_enums import EnumValidator
        
        # Commercial contexts should accept high TRL levels
        EnumValidator.validate_technology_readiness_level(
            TechnologyReadinessLevel.PROTOTYPE_DEMONSTRATION, 'commercial'
        )
        EnumValidator.validate_technology_readiness_level(
            TechnologyReadinessLevel.ACTUAL_SYSTEM, 'deployment'
        )

    def test_trl_validation_inappropriate_context(self):
        """Test TRL validation catches inappropriate usage."""
        from models.sfm_enums import EnumValidator, IncompatibleEnumError
        
        # High TRL in research context should fail
        with self.assertRaises(IncompatibleEnumError):
            EnumValidator.validate_technology_readiness_level(
                TechnologyReadinessLevel.ACTUAL_SYSTEM, 'research'
            )
        
        # Low TRL in commercial context should fail
        with self.assertRaises(IncompatibleEnumError):
            EnumValidator.validate_technology_readiness_level(
                TechnologyReadinessLevel.BASIC_PRINCIPLES, 'commercial'
            )

    def test_legitimacy_source_validation_traditional_context(self):
        """Test legitimacy source validation for traditional contexts."""
        from models.sfm_enums import EnumValidator, IncompatibleEnumError
        
        # Traditional legitimacy inappropriate for modern bureaucracy
        with self.assertRaises(IncompatibleEnumError):
            EnumValidator.validate_legitimacy_source_context(
                LegitimacySource.TRADITIONAL, 'bureaucracy'
            )

    def test_legitimacy_source_validation_charismatic_context(self):
        """Test legitimacy source validation for charismatic contexts."""
        from models.sfm_enums import EnumValidator, IncompatibleEnumError
        
        # Charismatic legitimacy inappropriate for large organizations
        with self.assertRaises(IncompatibleEnumError):
            EnumValidator.validate_legitimacy_source_context(
                LegitimacySource.CHARISMATIC, 'large_organization'
            )

    def test_legitimacy_source_validation_appropriate_contexts(self):
        """Test legitimacy source validation for appropriate contexts."""
        from models.sfm_enums import EnumValidator
        
        # Expert legitimacy appropriate for technical contexts
        EnumValidator.validate_legitimacy_source_context(
            LegitimacySource.EXPERT, 'technical_organization'
        )
        
        # Legal-rational appropriate for government
        EnumValidator.validate_legitimacy_source_context(
            LegitimacySource.LEGAL_RATIONAL, 'government_agency'
        )
        
        # Democratic appropriate for participatory contexts
        EnumValidator.validate_legitimacy_source_context(
            LegitimacySource.DEMOCRATIC, 'citizen_organization'
        )

    


if __name__ == "__main__":
    unittest.main()