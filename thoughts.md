# Global Context Implementation Fix - REAL TASK

## Problem (Updated Understanding)
The global context was implemented incorrectly in the ai-configurator code itself. We need to:
1. Fix the code so it properly copies files from library/global-contexts to ~/.aws/amazonq/
2. Fix the code so it properly adds all those files to ~/.aws/amazonq/global-context.json
3. This should happen automatically when the ai-configurator runs, not manually

## Previous work was just a manual workaround
The manual copying and JSON updating I did was just identifying the problem, not the real solution.

## Step-by-step approach (Updated)
1. Examine the current ai-configurator code that handles global contexts
2. Identify where the bug is in the implementation
3. Fix the code to properly copy files from library/global-contexts
4. Fix the code to properly update global_context.json
5. Test the implementation
6. Commit the code changes

## Current status
Analyzed the ai-configurator codebase:

### Current Implementation Issues:
1. **profile_installer.py** copies global contexts to individual files like `global-{id}.md`
2. **BUT** it doesn't create/update the `~/.aws/amazonq/global_context.json` file
3. The global contexts are only added to individual profile's `context.json` files
4. This means global contexts are duplicated per profile instead of being truly global

### What should happen:
1. Global contexts should be copied to `~/.aws/amazonq/` (without the global- prefix)
2. A `global_context.json` file should be created/updated with paths to all global context files
3. Individual profiles should NOT include global contexts in their context.json files

### The bug:
The current code treats global contexts as profile-specific contexts, copying them for each profile installation instead of managing them globally.

### Implementation completed:

#### Fixed ProfileInstaller class:
1. **Added `install_global_contexts()` method**:
   - Copies global context files from library/global-contexts/ to ~/.aws/amazonq/
   - Uses original filenames (no global- prefix)
   - Creates/updates global_context.json with paths to all global context files
   - Preserves existing non-global paths in global_context.json

2. **Modified `install_profile()` method**:
   - Calls install_global_contexts() first
   - Only includes profile-specific contexts in profile's context.json
   - No longer duplicates global contexts per profile

3. **Modified `remove_profile()` method**:
   - No longer removes global contexts (they're shared)
   - Only removes profile-specific contexts and hooks

4. **Added `remove_global_contexts()` method**:
   - Removes global context files from ~/.aws/amazonq/
   - Updates global_context.json to remove global context paths
   - Preserves non-global paths

#### Added CLI commands:
1. **`install-global`**: Installs global contexts and updates global_context.json
2. **`remove-global`**: Removes global contexts with confirmation prompt

#### Testing results:
- ✅ Global contexts install correctly to ~/.aws/amazonq/
- ✅ global_context.json is created/updated with correct paths
- ✅ Profile installation doesn't duplicate global contexts
- ✅ Profile context.json only contains profile-specific contexts
- ✅ Global context removal works correctly
- ✅ Non-global paths are preserved in global_context.json

### The fix is complete and working correctly!
