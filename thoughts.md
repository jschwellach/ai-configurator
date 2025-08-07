# Global Context Implementation Fix

## Problem
The global context was implemented incorrectly. We need to:
1. Copy files from library/global-context to ~/.aws/amazonq/
2. Add all those files to ~/.aws/amazonq/global-context.json

## Step-by-step approach
1. Examine current directory structure
2. Check what's in library/global-context
3. Check current state of ~/.aws/amazonq/global-context.json
4. Copy files from library/global-context to ~/.aws/amazonq/
5. Update global-context.json to include all copied files
6. Test the implementation
7. Commit changes with git

## Current status
Investigation complete:

### Findings:
1. library/global-contexts contains 4 files:
   - aws-security-best-practices.md
   - organizational-policies.md  
   - common-abbreviations.md
   - defaults.md

2. ~/.aws/amazonq/global_context.json exists (with underscore) and currently contains:
   ```json
   {
     "paths": [
       "/home/jschwellach/.aws/amazonq/contexts/basic.md"
     ],
     "hooks": {}
   }
   ```

3. Need to:
   - Copy the 4 files from library/global-contexts to ~/.aws/amazonq/
   - Add their paths to the global_context.json file

### Next steps:
1. ✅ Copy files - COMPLETED
2. ✅ Update global_context.json - COMPLETED  
3. Test and commit - IN PROGRESS

### Implementation completed:
- Copied 4 files from library/global-contexts/ to ~/.aws/amazonq/
- Updated ~/.aws/amazonq/global_context.json to include all files:
  - /home/jschwellach/.aws/amazonq/contexts/basic.md (existing)
  - /home/jschwellach/.aws/amazonq/aws-security-best-practices.md (new)
  - /home/jschwellach/.aws/amazonq/organizational-policies.md (new)
  - /home/jschwellach/.aws/amazonq/common-abbreviations.md (new)
  - /home/jschwellach/.aws/amazonq/defaults.md (new)

### Testing:
- Verified all files copied successfully
- Verified global_context.json updated correctly
- Files are accessible and contain expected content

Ready to commit changes.
