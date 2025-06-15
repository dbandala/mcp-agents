# filepath: /Users/bandala/Documents/bandala/code/mcp-agents/mcp_servers_py/blender_expert/tools/advisor.py
"""
Blender Advisor Module

This module provides expert analysis and suggestions for Blender models and scenes.
It includes topology health checks, scene optimization hints, and modifier stack reviews.
"""

import json
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum


class SeverityLevel(Enum):
    """Severity levels for advisor suggestions"""
    INFO = "info"
    WARNING = "warning" 
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Suggestion:
    """Represents a single advisor suggestion"""
    category: str
    severity: SeverityLevel
    title: str
    description: str
    solution: str
    affected_objects: Optional[List[str]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category,
            "severity": self.severity.value,
            "title": self.title,
            "description": self.description,
            "solution": self.solution,
            "affected_objects": self.affected_objects or []
        }


class BlenderAdvisor:
    """
    Expert advisor for Blender scenes and models.
    Provides topology health checks, optimization hints, and modifier reviews.
    """
    
    def __init__(self):
        self.suggestions = []
        
    def analyze_scene(self, scene_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive scene analysis combining all advisor features.
        
        Args:
            scene_data: Dictionary containing scene information from Blender
            
        Returns:
            Dictionary with analysis results and suggestions
        """
        self.suggestions = []
        
        # Perform all analysis types
        topology_results = self.check_topology_health(scene_data)
        optimization_results = self.get_optimization_hints(scene_data)
        modifier_results = self.review_modifier_stack(scene_data)
        
        # Combine results
        analysis_results = {
            "summary": self._generate_summary(),
            "topology_health": topology_results,
            "optimization_hints": optimization_results,
            "modifier_review": modifier_results,
            "all_suggestions": [s.to_dict() for s in self.suggestions],
            "severity_counts": self._count_severity_levels()
        }
        
        return analysis_results
    
    def check_topology_health(self, scene_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyzes mesh topology health for all objects in the scene.
        
        Args:
            scene_data: Scene data containing object information
            
        Returns:
            Dictionary with topology health analysis
        """
        topology_issues = []
        
        objects = scene_data.get("objects", [])
        
        for obj in objects:
            if obj.get("type") != "MESH":
                continue
                
            obj_name = obj.get("name", "Unknown")
            mesh_data = obj.get("mesh_data", {})
            
            # Check for common topology issues
            issues = self._check_mesh_topology(obj_name, mesh_data)
            topology_issues.extend(issues)
        
        return {
            "total_issues": len(topology_issues),
            "issues_by_object": self._group_issues_by_object(topology_issues),
            "recommendations": self._get_topology_recommendations(topology_issues)
        }
    
    def _check_mesh_topology(self, obj_name: str, mesh_data: Dict[str, Any]) -> List[Suggestion]:
        """Check specific topology issues for a mesh object"""
        issues = []
        
        vertex_count = mesh_data.get("vertex_count", 0)
        face_count = mesh_data.get("face_count", 0)
        edge_count = mesh_data.get("edge_count", 0)
        
        # Check for high poly count
        if vertex_count > 100000:
            issues.append(Suggestion(
                category="topology",
                severity=SeverityLevel.WARNING,
                title="High Polygon Count",
                description=f"Object '{obj_name}' has {vertex_count:,} vertices, which may impact performance.",
                solution="Consider using a Decimate modifier or retopology for better performance.",
                affected_objects=[obj_name]
            ))
        
        # Check for potential non-manifold geometry
        if mesh_data.get("has_loose_vertices", False):
            issues.append(Suggestion(
                category="topology",
                severity=SeverityLevel.ERROR,
                title="Loose Vertices Detected",
                description=f"Object '{obj_name}' contains loose vertices that are not connected to any faces.",
                solution="Use Mesh > Clean up > Delete Loose to remove disconnected vertices.",
                affected_objects=[obj_name]
            ))
        
        # Check for triangulated faces in modeling context
        triangle_ratio = mesh_data.get("triangle_ratio", 0.0)
        if triangle_ratio > 0.8 and mesh_data.get("intended_for", "") != "game":
            issues.append(Suggestion(
                category="topology",
                severity=SeverityLevel.INFO,
                title="High Triangle Density",
                description=f"Object '{obj_name}' is {triangle_ratio*100:.1f}% triangulated.",
                solution="Consider using quads for better subdivision and modeling workflow.",
                affected_objects=[obj_name]
            ))
        
        # Check for degenerate faces
        if mesh_data.get("has_degenerate_faces", False):
            issues.append(Suggestion(
                category="topology",
                severity=SeverityLevel.ERROR,
                title="Degenerate Faces Found",
                description=f"Object '{obj_name}' contains faces with zero area or invalid topology.",
                solution="Use Mesh > Clean up > Degenerate Dissolve to fix invalid faces.",
                affected_objects=[obj_name]
            ))
        
        # Check edge flow for subdivision surfaces
        if mesh_data.get("has_subdivision_surface", False) and mesh_data.get("bad_edge_flow", False):
            issues.append(Suggestion(
                category="topology",
                severity=SeverityLevel.WARNING,
                title="Poor Edge Flow",
                description=f"Object '{obj_name}' has subdivision surfaces but poor edge flow.",
                solution="Improve edge loops to follow the natural form and muscle flow.",
                affected_objects=[obj_name]
            ))
        
        self.suggestions.extend(issues)
        return issues
    
    def get_optimization_hints(self, scene_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provides scene optimization suggestions for better performance.
        
        Args:
            scene_data: Scene data to analyze
            
        Returns:
            Dictionary with optimization recommendations
        """
        optimization_suggestions = []
        
        # Analyze render settings
        render_settings = scene_data.get("render_settings", {})
        optimization_suggestions.extend(self._analyze_render_settings(render_settings))
        
        # Analyze material usage
        materials = scene_data.get("materials", [])
        optimization_suggestions.extend(self._analyze_materials(materials))
        
        # Analyze scene complexity
        objects = scene_data.get("objects", [])
        optimization_suggestions.extend(self._analyze_scene_complexity(objects))
        
        # Analyze texture usage
        textures = scene_data.get("textures", [])
        optimization_suggestions.extend(self._analyze_textures(textures))
        
        return {
            "total_suggestions": len(optimization_suggestions),
            "performance_impact": self._calculate_performance_impact(optimization_suggestions),
            "priority_optimizations": self._get_priority_optimizations(optimization_suggestions)
        }
    
    def _analyze_render_settings(self, render_settings: Dict[str, Any]) -> List[Suggestion]:
        """Analyze render settings for optimization opportunities"""
        suggestions = []
        
        # Check sample count
        samples = render_settings.get("samples", 0)
        if samples > 1000:
            suggestions.append(Suggestion(
                category="optimization",
                severity=SeverityLevel.WARNING,
                title="High Sample Count",
                description=f"Render samples set to {samples}, which may cause long render times.",
                solution="Consider using denoising and lower sample counts (128-512) for faster renders.",
                affected_objects=["Render Settings"]
            ))
        
        # Check resolution
        resolution_x = render_settings.get("resolution_x", 1920)
        resolution_y = render_settings.get("resolution_y", 1080)
        if resolution_x * resolution_y > 8294400:  # 4K
            suggestions.append(Suggestion(
                category="optimization",
                severity=SeverityLevel.INFO,
                title="High Resolution Render",
                description=f"Render resolution is {resolution_x}x{resolution_y}.",
                solution="Consider rendering at lower resolution for previews and tests.",
                affected_objects=["Render Settings"]
            ))
        
        # Check for unnecessary effects
        if render_settings.get("motion_blur", False) and render_settings.get("motion_blur_samples", 1) > 5:
            suggestions.append(Suggestion(
                category="optimization",
                severity=SeverityLevel.INFO,
                title="High Motion Blur Samples",
                description="Motion blur samples are set high, impacting render time.",
                solution="Reduce motion blur samples or disable for static scenes.",
                affected_objects=["Render Settings"]
            ))
        
        self.suggestions.extend(suggestions)
        return suggestions
    
    def _analyze_materials(self, materials: List[Dict[str, Any]]) -> List[Suggestion]:
        """Analyze materials for optimization"""
        suggestions = []
        
        # Check for unused materials
        unused_materials = [mat for mat in materials if mat.get("users", 0) == 0]
        if unused_materials:
            suggestions.append(Suggestion(
                category="optimization",
                severity=SeverityLevel.INFO,
                title="Unused Materials",
                description=f"Found {len(unused_materials)} unused materials taking up memory.",
                solution="Remove unused materials with File > Clean Up > Unused Data-Blocks.",
                affected_objects=[mat.get("name", "Unknown") for mat in unused_materials]
            ))
        
        # Check for overly complex materials
        complex_materials = []
        for mat in materials:
            node_count = mat.get("node_count", 0)
            if node_count > 50:
                complex_materials.append(mat.get("name", "Unknown"))
        
        if complex_materials:
            suggestions.append(Suggestion(
                category="optimization",
                severity=SeverityLevel.WARNING,
                title="Complex Materials",
                description=f"Materials with many nodes detected: {', '.join(complex_materials)}",
                solution="Simplify node trees or use material groups for better performance.",
                affected_objects=complex_materials
            ))
        
        self.suggestions.extend(suggestions)
        return suggestions
    
    def _analyze_scene_complexity(self, objects: List[Dict[str, Any]]) -> List[Suggestion]:
        """Analyze overall scene complexity"""
        suggestions = []
        
        total_vertices = sum(obj.get("mesh_data", {}).get("vertex_count", 0) 
                           for obj in objects if obj.get("type") == "MESH")
        
        if total_vertices > 1000000:
            suggestions.append(Suggestion(
                category="optimization",
                severity=SeverityLevel.WARNING,
                title="High Scene Complexity",
                description=f"Scene has {total_vertices:,} total vertices.",
                solution="Use levels of detail, instancing, or proxy objects for distant geometry.",
                affected_objects=["Scene"]
            ))
        
        # Check for too many objects
        if len(objects) > 1000:
            suggestions.append(Suggestion(
                category="optimization",
                severity=SeverityLevel.WARNING,
                title="Many Objects",
                description=f"Scene contains {len(objects)} objects.",
                solution="Consider joining similar objects or using collections more effectively.",
                affected_objects=["Scene"]
            ))
        
        self.suggestions.extend(suggestions)
        return suggestions
    
    def _analyze_textures(self, textures: List[Dict[str, Any]]) -> List[Suggestion]:
        """Analyze texture usage for optimization"""
        suggestions = []
        
        # Check for large textures
        large_textures = []
        total_memory = 0
        
        for texture in textures:
            width = texture.get("width", 0)
            height = texture.get("height", 0)
            memory_mb = (width * height * 4) / (1024 * 1024)  # Rough estimate for RGBA
            total_memory += memory_mb
            
            if width > 4096 or height > 4096:
                large_textures.append(texture.get("name", "Unknown"))
        
        if large_textures:
            suggestions.append(Suggestion(
                category="optimization",
                severity=SeverityLevel.WARNING,
                title="Large Textures",
                description=f"Large textures detected: {', '.join(large_textures)}",
                solution="Consider reducing texture resolution or using texture compression.",
                affected_objects=large_textures
            ))
        
        if total_memory > 500:  # 500MB
            suggestions.append(Suggestion(
                category="optimization",
                severity=SeverityLevel.WARNING,
                title="High Texture Memory Usage",
                description=f"Estimated texture memory usage: {total_memory:.1f}MB",
                solution="Optimize texture sizes and consider texture atlasing.",
                affected_objects=["Scene"]
            ))
        
        self.suggestions.extend(suggestions)
        return suggestions
    
    def review_modifier_stack(self, scene_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Reviews modifier stacks for all objects and provides recommendations.
        
        Args:
            scene_data: Scene data containing object information
            
        Returns:
            Dictionary with modifier stack analysis
        """
        modifier_suggestions = []
        
        objects = scene_data.get("objects", [])
        
        for obj in objects:
            obj_name = obj.get("name", "Unknown")
            modifiers = obj.get("modifiers", [])
            
            if not modifiers:
                continue
                
            suggestions = self._analyze_modifier_stack(obj_name, modifiers)
            modifier_suggestions.extend(suggestions)
        
        return {
            "total_suggestions": len(modifier_suggestions),
            "objects_with_modifiers": len([obj for obj in objects if obj.get("modifiers")]),
            "common_issues": self._get_common_modifier_issues(modifier_suggestions),
            "optimization_opportunities": self._get_modifier_optimizations(modifier_suggestions)
        }
    
    def _analyze_modifier_stack(self, obj_name: str, modifiers: List[Dict[str, Any]]) -> List[Suggestion]:
        """Analyze modifier stack for a specific object"""
        suggestions = []
        
        # Check modifier order
        suggestions.extend(self._check_modifier_order(obj_name, modifiers))
        
        # Check for inefficient modifiers
        suggestions.extend(self._check_inefficient_modifiers(obj_name, modifiers))
        
        # Check for unnecessary modifiers
        suggestions.extend(self._check_unnecessary_modifiers(obj_name, modifiers))
        
        # Check for performance issues
        suggestions.extend(self._check_modifier_performance(obj_name, modifiers))
        
        self.suggestions.extend(suggestions)
        return suggestions
    
    def _check_modifier_order(self, obj_name: str, modifiers: List[Dict[str, Any]]) -> List[Suggestion]:
        """Check for suboptimal modifier order"""
        suggestions = []
        
        # Common order issues
        modifier_types = [mod.get("type", "") for mod in modifiers]
        
        # Subdivision Surface should generally be last
        if "SUBSURF" in modifier_types:
            subsurf_index = modifier_types.index("SUBSURF")
            if subsurf_index < len(modifier_types) - 1:
                later_modifiers = modifier_types[subsurf_index + 1:]
                if any(mod_type in ["BEVEL", "EDGE_SPLIT"] for mod_type in later_modifiers):
                    suggestions.append(Suggestion(
                        category="modifiers",
                        severity=SeverityLevel.WARNING,
                        title="Suboptimal Modifier Order",
                        description=f"Object '{obj_name}' has Subdivision Surface before Bevel/Edge Split.",
                        solution="Move Subdivision Surface after edge-affecting modifiers for better results.",
                        affected_objects=[obj_name]
                    ))
        
        # Mirror modifier should be early
        if "MIRROR" in modifier_types:
            mirror_index = modifier_types.index("MIRROR")
            if mirror_index > 2:
                suggestions.append(Suggestion(
                    category="modifiers",
                    severity=SeverityLevel.INFO,
                    title="Late Mirror Modifier",
                    description=f"Object '{obj_name}' has Mirror modifier late in the stack.",
                    solution="Consider moving Mirror modifier earlier for better workflow.",
                    affected_objects=[obj_name]
                ))
        
        return suggestions
    
    def _check_inefficient_modifiers(self, obj_name: str, modifiers: List[Dict[str, Any]]) -> List[Suggestion]:
        """Check for inefficient modifier configurations"""
        suggestions = []
        
        for modifier in modifiers:
            mod_type = modifier.get("type", "")
            mod_name = modifier.get("name", "Unknown")
            
            # Check Array modifier efficiency
            if mod_type == "ARRAY":
                count = modifier.get("count", 1)
                if count > 100:
                    suggestions.append(Suggestion(
                        category="modifiers",
                        severity=SeverityLevel.WARNING,
                        title="High Array Count",
                        description=f"Array modifier '{mod_name}' on '{obj_name}' has {count} copies.",
                        solution="Consider using geometry nodes or instancing for large arrays.",
                        affected_objects=[obj_name]
                    ))
            
            # Check Subdivision Surface levels
            if mod_type == "SUBSURF":
                render_levels = modifier.get("render_levels", 2)
                viewport_levels = modifier.get("levels", 2)
                
                if render_levels > 3:
                    suggestions.append(Suggestion(
                        category="modifiers",
                        severity=SeverityLevel.WARNING,
                        title="High Subdivision Levels",
                        description=f"Subdivision Surface '{mod_name}' on '{obj_name}' has {render_levels} render levels.",
                        solution="High subdivision levels exponentially increase geometry. Consider lower levels.",
                        affected_objects=[obj_name]
                    ))
                
                if viewport_levels > 2:
                    suggestions.append(Suggestion(
                        category="modifiers",
                        severity=SeverityLevel.INFO,
                        title="High Viewport Subdivision",
                        description=f"High viewport subdivision on '{obj_name}' may impact performance.",
                        solution="Lower viewport subdivision levels for better interactive performance.",
                        affected_objects=[obj_name]
                    ))
        
        return suggestions
    
    def _check_unnecessary_modifiers(self, obj_name: str, modifiers: List[Dict[str, Any]]) -> List[Suggestion]:
        """Check for potentially unnecessary modifiers"""
        suggestions = []
        
        # Check for disabled modifiers
        disabled_modifiers = [mod for mod in modifiers if not mod.get("show_viewport", True)]
        if disabled_modifiers:
            suggestions.append(Suggestion(
                category="modifiers",
                severity=SeverityLevel.INFO,
                title="Disabled Modifiers",
                description=f"Object '{obj_name}' has {len(disabled_modifiers)} disabled modifiers.",
                solution="Remove unused modifiers to clean up the modifier stack.",
                affected_objects=[obj_name]
            ))
        
        # Check for duplicate modifier types
        modifier_types = [mod.get("type", "") for mod in modifiers]
        duplicate_types = [mod_type for mod_type in set(modifier_types) if modifier_types.count(mod_type) > 1]
        
        if duplicate_types:
            suggestions.append(Suggestion(
                category="modifiers",
                severity=SeverityLevel.INFO,
                title="Duplicate Modifier Types",
                description=f"Object '{obj_name}' has multiple modifiers of types: {', '.join(duplicate_types)}",
                solution="Consider combining similar modifiers or verifying their necessity.",
                affected_objects=[obj_name]
            ))
        
        return suggestions
    
    def _check_modifier_performance(self, obj_name: str, modifiers: List[Dict[str, Any]]) -> List[Suggestion]:
        """Check for performance-impacting modifier configurations"""
        suggestions = []
        
        # Check for expensive modifier combinations
        modifier_types = [mod.get("type", "") for mod in modifiers]
        
        if "SUBSURF" in modifier_types and len(modifier_types) > 5:
            suggestions.append(Suggestion(
                category="modifiers",
                severity=SeverityLevel.WARNING,
                title="Heavy Modifier Stack",
                description=f"Object '{obj_name}' has {len(modifier_types)} modifiers including Subdivision Surface.",
                solution="Consider applying some modifiers or using simpler alternatives for better performance.",
                affected_objects=[obj_name]
            ))
        
        # Check for simulation modifiers
        simulation_modifiers = ["CLOTH", "SOFT_BODY", "FLUID", "SMOKE", "DYNAMIC_PAINT"]
        active_simulations = [mod_type for mod_type in modifier_types if mod_type in simulation_modifiers]
        
        if len(active_simulations) > 1:
            suggestions.append(Suggestion(
                category="modifiers",
                severity=SeverityLevel.WARNING,
                title="Multiple Simulations",
                description=f"Object '{obj_name}' has multiple simulation modifiers: {', '.join(active_simulations)}",
                solution="Multiple simulations can be very performance intensive. Consider baking or simplifying.",
                affected_objects=[obj_name]
            ))
        
        return suggestions
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate a summary of the analysis"""
        severity_counts = self._count_severity_levels()
        
        return {
            "total_suggestions": len(self.suggestions),
            "severity_breakdown": severity_counts,
            "health_score": self._calculate_health_score(),
            "top_priorities": [s.to_dict() for s in self.suggestions if s.severity in [SeverityLevel.ERROR, SeverityLevel.CRITICAL]][:5]
        }
    
    def _count_severity_levels(self) -> Dict[str, int]:
        """Count suggestions by severity level"""
        counts = {level.value: 0 for level in SeverityLevel}
        for suggestion in self.suggestions:
            counts[suggestion.severity.value] += 1
        return counts
    
    def _calculate_health_score(self) -> int:
        """Calculate a health score from 0-100 based on issues found"""
        if not self.suggestions:
            return 100
        
        severity_weights = {
            SeverityLevel.CRITICAL: 25,
            SeverityLevel.ERROR: 15,
            SeverityLevel.WARNING: 8,
            SeverityLevel.INFO: 2
        }
        
        total_penalty = sum(severity_weights.get(s.severity, 0) for s in self.suggestions)
        health_score = max(0, 100 - total_penalty)
        
        return health_score
    
    def _group_issues_by_object(self, issues: List[Suggestion]) -> Dict[str, List[Dict[str, Any]]]:
        """Group issues by affected objects"""
        grouped = {}
        for issue in issues:
            for obj_name in issue.affected_objects or ["General"]:
                if obj_name not in grouped:
                    grouped[obj_name] = []
                grouped[obj_name].append(issue.to_dict())
        return grouped
    
    def _get_topology_recommendations(self, issues: List[Suggestion]) -> List[str]:
        """Get general topology recommendations"""
        recommendations = [
            "Use quads for better subdivision and modeling workflow",
            "Keep polygon count appropriate for the intended use",
            "Maintain clean edge flow for character models",
            "Avoid n-gons in areas that will be subdivided",
            "Use consistent topology density across the model"
        ]
        return recommendations
    
    def _calculate_performance_impact(self, suggestions: List[Suggestion]) -> str:
        """Estimate performance impact level"""
        high_impact = sum(1 for s in suggestions if s.severity in [SeverityLevel.ERROR, SeverityLevel.CRITICAL])
        medium_impact = sum(1 for s in suggestions if s.severity == SeverityLevel.WARNING)
        
        if high_impact > 3:
            return "High"
        elif medium_impact > 5:
            return "Medium"
        else:
            return "Low"
    
    def _get_priority_optimizations(self, suggestions: List[Suggestion]) -> List[Dict[str, Any]]:
        """Get the highest priority optimization suggestions"""
        priority_suggestions = [s for s in suggestions if s.severity in [SeverityLevel.ERROR, SeverityLevel.WARNING]]
        return [s.to_dict() for s in priority_suggestions[:3]]
    
    def _get_common_modifier_issues(self, suggestions: List[Suggestion]) -> List[str]:
        """Identify common modifier issues"""
        issue_types = []
        for suggestion in suggestions:
            if "order" in suggestion.title.lower():
                issue_types.append("Modifier order")
            elif "subdivision" in suggestion.title.lower():
                issue_types.append("Subdivision levels")
            elif "array" in suggestion.title.lower():
                issue_types.append("Array efficiency")
        
        return list(set(issue_types))
    
    def _get_modifier_optimizations(self, suggestions: List[Suggestion]) -> List[str]:
        """Get modifier optimization opportunities"""
        optimizations = [
            "Apply modifiers that won't be changed",
            "Use simpler alternatives for viewport",
            "Optimize subdivision levels",
            "Consider geometry nodes for complex operations"
        ]
        return optimizations


# Convenience function for external use
def analyze_blender_scene(scene_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to analyze a Blender scene.
    
    Args:
        scene_data: Dictionary containing scene information from Blender
        
    Returns:
        Dictionary with comprehensive analysis results
    """
    advisor = BlenderAdvisor()
    return advisor.analyze_scene(scene_data)


def get_topology_health_check(scene_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Perform only topology health check.
    
    Args:
        scene_data: Dictionary containing scene information from Blender
        
    Returns:
        Dictionary with topology analysis results
    """
    advisor = BlenderAdvisor()
    return advisor.check_topology_health(scene_data)


def get_optimization_hints(scene_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get only optimization hints.
    
    Args:
        scene_data: Dictionary containing scene information from Blender
        
    Returns:
        Dictionary with optimization suggestions
    """
    advisor = BlenderAdvisor()
    return advisor.get_optimization_hints(scene_data)


def review_modifier_stacks(scene_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Review only modifier stacks.
    
    Args:
        scene_data: Dictionary containing scene information from Blender
        
    Returns:
        Dictionary with modifier stack analysis
    """
    advisor = BlenderAdvisor()
    return advisor.review_modifier_stack(scene_data)