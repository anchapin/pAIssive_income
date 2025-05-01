"""
Script to fix failing tests in the pAIssive_income project.
"""

import os
import sys
import re
from typing import List, Dict, Any, Optional, Tuple

def fix_fallback_strategy():
    """Fix the fallback strategy implementation."""
    file_path = "ai_models/fallbacks/fallback_strategy.py"

    # Read the file
    with open(file_path, "r") as f:
        content = f.read()

    # Fix 1: Update the cascade order to include SIZE_TIER
    cascade_order_pattern = r"cascade_order = \[\s*FallbackStrategy\.DEFAULT,\s*FallbackStrategy\.SIMILAR_MODEL,\s*FallbackStrategy\.MODEL_TYPE,\s*FallbackStrategy\.CAPABILITY_BASED,\s*FallbackStrategy\.SPECIFIED_LIST,\s*FallbackStrategy\.ANY_AVAILABLE\s*\]"
    cascade_order_replacement = """cascade_order = [
            FallbackStrategy.DEFAULT,
            FallbackStrategy.SIMILAR_MODEL,
            FallbackStrategy.MODEL_TYPE,
            FallbackStrategy.SIZE_TIER,
            FallbackStrategy.CAPABILITY_BASED,
            FallbackStrategy.SPECIFIED_LIST,
            FallbackStrategy.ANY_AVAILABLE
        ]"""
    content = re.sub(cascade_order_pattern, cascade_order_replacement, content)

    # Fix 2: Update the _apply_size_tier_strategy method to handle None values
    size_tier_pattern = r"def _apply_size_tier_strategy\(.*?\):.*?# If still no match, return any model.*?return candidates\[0\]"
    size_tier_replacement = """def _apply_size_tier_strategy(
        self, original_model: Optional[IModelInfo]
    ) -> Optional[IModelInfo]:
        \"\"\"Try models of different size tiers, preferring smaller models as fallbacks.\"\"\"
        # This strategy works best when we have size information for models
        all_models = self.model_manager.get_all_models()

        # If no original model, just return any model
        if not original_model:
            return all_models[0] if all_models else None

        # Filter out the original model
        candidates = [m for m in all_models if m.id != original_model.id]
        if not candidates:
            return None

        # If original model has no size information, we can't do size-based fallback
        if not hasattr(original_model, "size_mb") or original_model.size_mb is None:
            # Fall back to similar model strategy
            return self._apply_similar_model_strategy(original_model)

        # Get original model size
        original_size = original_model.size_mb

        # Find models smaller than the original
        smaller_models = [
            m for m in candidates
            if hasattr(m, "size_mb") and m.size_mb is not None and m.size_mb < original_size
        ]

        # If we have smaller models, return the largest of them
        if smaller_models:
            # Sort by size (descending)
            smaller_models.sort(key=lambda m: m.size_mb or 0, reverse=True)
            return smaller_models[0]

        # If no smaller models, try to find a model of similar size
        similar_size_models = [
            m for m in candidates
            if hasattr(m, "size_mb") and m.size_mb is not None
        ]

        if similar_size_models:
            # Sort by size difference (ascending)
            similar_size_models.sort(key=lambda m: abs((m.size_mb or 0) - original_size))
            return similar_size_models[0]

        # If still no match, return any model
        return candidates[0]"""

    content = re.sub(size_tier_pattern, size_tier_replacement, content, flags=re.DOTALL)

    # Write the updated content back to the file
    with open(file_path, "w") as f:
        f.write(content)

    print(f"Fixed fallback strategy implementation in {file_path}")


def fix_memory_cache():
    """Fix the memory cache implementation."""
    file_path = "ai_models/caching/cache_backends/memory_cache.py"

    # Read the file
    with open(file_path, "r") as f:
        content = f.read()

    # Fix the _evict_item method to properly implement LRU eviction
    evict_item_pattern = r"def _evict_item\(self\) -> None:.*?self\.stats\[\"evictions\"\] \+= 1\s*self\.stats\[\"deletes\"\] \+= 1"
    evict_item_replacement = """def _evict_item(self) -> None:
        \"\"\"Evict an item based on the eviction policy.\"\"\"
        with self.lock:
            if not self.cache:
                return

            current_time = time.time()

            # Filter out expired items first
            valid_items = {
                k: v for k, v in self.cache.items()
                if v[1] is None or v[1] > current_time
            }

            if not valid_items:
                return

            if self.eviction_policy == "lru":
                # Get least recently accessed key
                key_to_evict = min(valid_items.items(), key=lambda x: x[1][3])[0]
            elif self.eviction_policy == "lfu":
                # Get least frequently used key
                key_to_evict = min(valid_items.items(), key=lambda x: (x[1][2], x[1][3]))[0]
            else:  # FIFO or default
                # Get oldest item by creation time (approximated by order in the dict)
                key_to_evict = next(iter(valid_items))

            if key_to_evict in self.cache:
                del self.cache[key_to_evict]
                self.stats["evictions"] += 1
                self.stats["deletes"] += 1"""

    content = re.sub(evict_item_pattern, evict_item_replacement, content, flags=re.DOTALL)

    # Write the updated content back to the file
    with open(file_path, "w") as f:
        f.write(content)

    print(f"Fixed memory cache implementation in {file_path}")


def fix_pydantic_warnings():
    """Fix Pydantic warnings about protected namespace conflicts."""
    # Find all model classes that use Pydantic
    model_files = [
        "ai_models/model_info.py",
        "ai_models/model_config.py",
        "ai_models/schemas.py",
    ]

    for file_path in model_files:
        if not os.path.exists(file_path):
            continue

        # Read the file
        with open(file_path, "r") as f:
            content = f.read()

        # Add model_config to disable protected namespaces
        if "model_config" not in content:
            # Find the class definition
            class_pattern = r"class (\w+)\(.*?\):"
            matches = re.findall(class_pattern, content)

            for class_name in matches:
                # Add model_config after the class definition
                class_def_pattern = f"class {class_name}\\(.*?\\):"
                class_def_replacement = f"class {class_name}(\\1):\n    model_config = {{'protected_namespaces': ()}}"

                content = re.sub(class_def_pattern, class_def_replacement, content)

        # Write the updated content back to the file
        with open(file_path, "w") as f:
            f.write(content)

        print(f"Fixed Pydantic warnings in {file_path}")


def fix_semver_warnings():
    """Fix semver deprecation warnings."""
    file_path = "ai_models/model_versioning.py"

    if not os.path.exists(file_path):
        return

    # Read the file
    with open(file_path, "r") as f:
        content = f.read()

    # Replace semver.parse with semver.Version.parse
    content = content.replace("semver.parse(", "semver.Version.parse(")

    # Write the updated content back to the file
    with open(file_path, "w") as f:
        f.write(content)

    print(f"Fixed semver warnings in {file_path}")


def main():
    """Main function to fix failing tests."""
    print("Fixing failing tests...")

    # Fix the fallback strategy implementation
    fix_fallback_strategy()

    # Fix the memory cache implementation
    fix_memory_cache()

    # Fix Pydantic warnings
    fix_pydantic_warnings()

    # Fix semver warnings
    fix_semver_warnings()

    print("Done fixing failing tests.")


if __name__ == "__main__":
    main()
