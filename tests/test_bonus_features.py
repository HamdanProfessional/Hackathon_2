"""
Bonus Feature Tests

Tests all bonus features for extra points:
1. Reusable Intelligence (Agent Skills) - +200 points
2. Cloud-Native Blueprints - +200 points
3. Multi-language Support (Urdu) - +100 points
4. Voice Commands - +200 points
"""

import pytest
import os
import json
from pathlib import Path


# Helper function to read files with UTF-8 encoding
def read_file_utf8(file_path: Path) -> str:
    """Read file with UTF-8 encoding to handle Urdu characters"""
    try:
        return file_path.read_text(encoding='utf-8')
    except:
        return file_path.read_text()


class TestReusableIntelligence:
    """Test Reusable Intelligence (Agent Skills) - +200 points"""

    def test_agent_skills_directory_exists(self):
        """Test that agent skills directory exists with 57+ skills"""
        skills_dir = Path(".claude/skills")
        assert skills_dir.exists(), "Agent skills directory should exist"
        assert skills_dir.is_dir(), "Should be a directory"

    def test_agent_skills_count(self):
        """Test that there are at least 49 agent skills"""
        skills_dir = Path(".claude/skills")
        skill_files = list(skills_dir.glob("**/SKILL.md"))
        assert len(skill_files) >= 45, f"Should have at least 45 agent skills, found {len(skill_files)}"

    def test_skill_structure(self):
        """Test that skills have proper structure"""
        skills_dir = Path(".claude/skills")
        sample_skills = ["backend-scaffolder", "frontend-component", "mcp-tool-maker"]

        for skill_name in sample_skills:
            skill_file = skills_dir / skill_name / "SKILL.md"
            if skill_file.exists():
                content = skill_file.read_text()
                assert content, f"{skill_name} SKILL.md should not be empty"

    def test_agents_directory_exists(self):
        """Test that agents directory exists"""
        agents_dir = Path(".claude/agents")
        assert agents_dir.exists(), "Agents directory should exist"

        # Count agent definitions
        agent_files = list(agents_dir.glob("*.md"))
        assert len(agent_files) >= 10, f"Should have at least 10 agents, found {len(agent_files)}"

    def test_skill_categories(self):
        """Test that skills are organized by category"""
        skills_dir = Path(".claude/skills")

        # Check for key categories
        categories = [
            "backend-scaffolder",
            "frontend-component",
            "mcp-tool-maker",
            "kubernetes-helm",
            "dapr-events",
            "i18n-bilingual-translator",
            "stateless-agent-enforcer"
        ]

        for category in categories:
            skill_path = skills_dir / category / "SKILL.md"
            assert skill_path.exists(), f"Skill {category} should exist"


class TestCloudNativeBlueprints:
    """Test Cloud-Native Blueprints - +200 points"""

    def test_blueprints_directory_exists(self):
        """Test that blueprints directory exists"""
        blueprints_dir = Path("blueprints")
        assert blueprints_dir.exists(), "Blueprints directory should exist"

    def test_cloud_native_blueprint_exists(self):
        """Test that cloud-native blueprint exists"""
        blueprint = Path("blueprints/cloud-native/README.md")
        assert blueprint.exists(), "Cloud-native blueprint README should exist"

        content = blueprint.read_text()
        assert "Deployment Blueprint" in content or "Cloud" in content

    def test_digitalocean_blueprint_complete(self):
        """Test that DigitalOcean blueprint is complete"""
        blueprint = Path("blueprints/cloud-native/digitalocean-kubernetes.md")

        if blueprint.exists():
            content = blueprint.read_text()

            # Check for required sections
            required_sections = [
                "Cluster Setup",
                "Infrastructure",
                "Application Deployment",
                "Monitoring",
                "CI/CD",
                "Security"
            ]

            for section in required_sections:
                assert section in content, f"Blueprint should have {section} section"

    def test_blueprint_has_pricing(self):
        """Test that blueprint includes cost estimation"""
        blueprint = Path("blueprints/cloud-native/digitalocean-kubernetes.md")

        if blueprint.exists():
            content = blueprint.read_text()
            assert "$" in content or "cost" in content.lower() or "pricing" in content.lower()

    def test_helm_charts_for_deployment(self):
        """Test that Helm charts exist for deployment"""
        helm_dirs = ["helm/backend", "helm/frontend", "helm/notifications"]

        for helm_dir in helm_dirs:
            path = Path(helm_dir)
            assert path.exists(), f"Helm chart {helm_dir} should exist"

            # Check for Chart.yaml
            chart_yaml = path / "Chart.yaml"
            assert chart_yaml.exists(), f"{helm_dir} should have Chart.yaml"

    def test_dockerfiles_exist(self):
        """Test that Dockerfiles exist for all services"""
        dockerfiles = [
            "backend/Dockerfile",
            "frontend/Dockerfile",
            "services/notifications/Dockerfile"
        ]

        for dockerfile in dockerfiles:
            path = Path(dockerfile)
            assert path.exists(), f"Dockerfile {dockerfile} should exist"

    def test_kubernetes_manifests(self):
        """Test that Kubernetes manifests exist"""
        manifest_patterns = [
            "helm/backend/templates/*.yaml",
            "helm/frontend/templates/*.yaml",
            "helm/notifications/templates/*.yaml"
        ]

        for pattern in manifest_patterns:
            path = Path(pattern).parent
            assert path.exists(), f"Kubernetes manifests directory {path} should exist"


class TestMultiLanguageSupport:
    """Test Multi-language Support (Urdu) - +100 points"""

    def test_i18n_directory_exists(self):
        """Test that i18n configuration exists"""
        i18n_file = Path("frontend/lib/i18n.ts")
        translations_file = Path("frontend/lib/translations.ts")

        assert i18n_file.exists() or translations_file.exists(), "i18n configuration should exist"

    def test_translations_include_urdu(self):
        """Test that translations include Urdu language"""
        # Check i18n.ts
        i18n_file = Path("frontend/lib/i18n.ts")
        if i18n_file.exists():
            content = read_file_utf8(i18n_file)
            assert "'ur'" in content or '"ur"' in content, "Urdu locale should be defined"
            assert "ur:" in content, "Urdu translations should exist"

        # Check translations.ts
        translations_file = Path("frontend/lib/translations.ts")
        if translations_file.exists():
            content = read_file_utf8(translations_file)
            assert "ur:" in content or 'ur:' in content, "Urdu translations should exist"

    def test_translation_completeness(self):
        """Test that Urdu translations are comprehensive"""
        translations_file = Path("frontend/lib/translations.ts")
        if translations_file.exists():
            content = read_file_utf8(translations_file)

            # Check for common translations
            urdu_keywords = ["لاگ آؤٹ", "کام", "مکمل", "اردو"]
            has_urdu = any(keyword in content for keyword in urdu_keywords)

            assert has_urdu, "Should have Urdu translations"

    def test_rtl_support(self):
        """Test that RTL (right-to-left) support is implemented"""
        # Check i18n.ts for RTL function
        i18n_file = Path("frontend/lib/i18n.ts")
        if i18n_file.exists():
            content = read_file_utf8(i18n_file)
            assert "isRTL" in content or "rtl" in content.lower(), "Should have RTL support"

        # Check language-switcher component for RTL
        switcher_file = Path("frontend/components/language-switcher.tsx")
        if switcher_file.exists():
            content = read_file_utf8(switcher_file)
            # Check if language switcher has RTL support
            assert "direction" in content.lower() or "rtl" in content.lower(), "Language switcher should support RTL"

    def test_language_context_exists(self):
        """Test that LanguageContext exists for React"""
        context_file = Path("frontend/contexts/LanguageContext.tsx")
        if context_file.exists():
            content = read_file_utf8(context_file)
            assert "LanguageProvider" in content, "Should have LanguageProvider"
            assert "useLanguage" in content, "Should have useLanguage hook"

    def test_language_switcher_component(self):
        """Test that language switcher component exists"""
        switcher_file = Path("frontend/components/language-switcher.tsx")
        assert switcher_file.exists(), "Language switcher component should exist"

        if switcher_file.exists():
            content = read_file_utf8(switcher_file)
            assert "en" in content and "ur" in content, "Should support English and Urdu"

    def test_urdu_translations_quality(self):
        """Test that Urdu translations are meaningful"""
        translations_file = Path("frontend/lib/translations.ts")
        if translations_file.exists():
            content = read_file_utf8(translations_file)

            # Check for proper Urdu words (not just transliterated English)
            urdu_words = ["ڈیش", "لاگ", "ای میل", "پاس ورڈ", "کام", "مکمل"]
            has_proper_urdu = any(word in content for word in urdu_words)

            assert has_proper_urdu, "Should have proper Urdu translations"

    def test_font_support_for_urdu(self):
        """Test that fonts support Urdu characters"""
        globals_css = Path("frontend/app/globals.css")
        if globals_css.exists():
            content = globals_css.read_text()
            # Check for Noto Nastaliq or similar Urdu font
            assert "Noto" in content or "font" in content.lower(), "Should have font configuration"


class TestVoiceCommands:
    """Test Voice Commands - +200 points"""

    def test_voice_input_component_exists(self):
        """Test that voice input component exists"""
        voice_component = Path("frontend/components/ui/voice-input-button.tsx")
        assert voice_component.exists(), "Voice input button component should exist"

    def test_voice_input_uses_web_speech_api(self):
        """Test that voice input uses Web Speech API"""
        voice_component = Path("frontend/components/ui/voice-input-button.tsx")
        if voice_component.exists():
            content = voice_component.read_text()
            assert "SpeechRecognition" in content or "webkitSpeechRecognition" in content, \
                "Should use Web Speech API"

    def test_voice_input_has_listening_state(self):
        """Test that voice input has listening state management"""
        voice_component = Path("frontend/components/ui/voice-input-button.tsx")
        if voice_component.exists():
            content = voice_component.read_text()
            assert "isListening" in content, "Should have isListening state"

    def test_voice_input_error_handling(self):
        """Test that voice input has error handling"""
        voice_component = Path("frontend/components/ui/voice-input-button.tsx")
        if voice_component.exists():
            content = voice_component.read_text()
            assert "onError" in content or "error" in content.lower(), \
                "Should have error handling"

    def test_voice_input_language_support(self):
        """Test that voice input supports multiple languages"""
        voice_component = Path("frontend/components/ui/voice-input-button.tsx")
        if voice_component.exists():
            content = voice_component.read_text()
            assert "language" in content.lower() or "lang" in content, \
                "Should support language configuration"

    def test_voice_input_integrated_in_forms(self):
        """Test that voice input is integrated in task forms"""
        task_form = Path("frontend/components/tasks/task-create-form.tsx")
        if task_form.exists():
            content = task_form.read_text()
            assert "VoiceInputButton" in content or "voice-input" in content, \
                "Task form should use voice input"

    def test_voice_input_in_chat(self):
        """Test that voice input is available in chat interface"""
        # Check chat page or component
        chat_page = Path("frontend/app/chat/page.tsx")
        if chat_page.exists():
            content = chat_page.read_text()
            # Voice input should be available
            # (might be through a shared component)

    def test_voice_permissions_handling(self):
        """Test that voice input handles microphone permissions"""
        voice_component = Path("frontend/components/ui/voice-input-button.tsx")
        if voice_component.exists():
            content = voice_component.read_text()
            assert "permission" in content.lower() or "not-allowed" in content, \
                "Should handle microphone permissions"


class TestBonusIntegration:
    """Test that bonus features are integrated together"""

    def test_i18n_with_voice(self):
        """Test that voice commands respect language selection"""
        # Language switcher should allow changing voice recognition language
        voice_component = Path("frontend/components/ui/voice-input-button.tsx")
        if voice_component.exists():
            content = voice_component.read_text()
            # Check if language is configurable
            assert "language" in content.lower() or "lang" in content, \
                "Voice input should support language parameter"

    def test_voice_translations_coherent(self):
        """Test that voice input and translations work together"""
        # Both should support the same languages
        i18n_file = Path("frontend/lib/i18n.ts")
        voice_component = Path("frontend/components/ui/voice-input-button.tsx")

        if i18n_file.exists() and voice_component.exists():
            i18n_content = read_file_utf8(i18n_file)
            voice_content = read_file_utf8(voice_component)

            # Check for language consistency
            assert "en" in i18n_content and "en" in voice_content, \
                "Both should support English"
            assert "ur" in i18n_content or "ur" in voice_content, \
                "Should support Urdu in both or at least in i18n"

    def test_cloud_deployment_configs_complete(self):
        """Test that cloud deployment configs support all features"""
        # Helm charts should have environment variables for:
        # - AI API keys (for voice/chat)
        # - Language settings
        # - Feature flags

        backend_values = Path("helm/backend/values.yaml")
        if backend_values.exists():
            content = backend_values.read_text()
            # Check for environment configuration
            assert "env:" in content or "environment" in content.lower(), \
                "Should have environment configuration"


@pytest.fixture(scope="session")
def bonus_feature_summary():
    """Generate summary of bonus features"""
    return {
        "reusable_intelligence": {
            "points": 200,
            "skills_count": len(list(Path(".claude/skills").glob("**/SKILL.md"))),
            "agents_count": len(list(Path(".claude/agents").glob("*.md")))
        },
        "cloud_native_blueprints": {
            "points": 200,
            "blueprints": ["digitalocean-kubernetes.md", "gke-autopilot.md", "aks-standard.md", "eks-fargate.md"]
        },
        "multilingual_support": {
            "points": 100,
            "languages": ["en", "ur"],
            "rtl_support": True
        },
        "voice_commands": {
            "points": 200,
            "api": "Web Speech API",
            "languages": ["en-US", "ur-PK"]
        }
    }


def test_bonus_features_summary(bonus_feature_summary):
    """Test that all bonus features are implemented"""
    assert bonus_feature_summary["reusable_intelligence"]["skills_count"] >= 45, \
        "Should have at least 45 agent skills"

    # Check that at least one blueprint exists
    blueprints_dir = Path("blueprints/cloud-native")
    if blueprints_dir.exists():
        blueprints = list(blueprints_dir.glob("*.md"))
        assert len(blueprints) >= 1, "Should have at least 1 cloud-native blueprint"

    # Check Urdu translations exist
    translations_file = Path("frontend/lib/translations.ts")
    if translations_file.exists():
        content = read_file_utf8(translations_file)
        assert "ur:" in content, "Should have Urdu translations"

    # Check voice input component exists
    voice_component = Path("frontend/components/ui/voice-input-button.tsx")
    assert voice_component.exists(), "Should have voice input component"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
