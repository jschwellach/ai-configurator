{
  "conversation_id": "d503e8f7-92de-4fd0-bba1-24becaca588b",
  "next_message": null,
  "history": [
    [
      {
        "additional_context": "",
        "env_context": {
          "env_state": {
            "operating_system": "macos",
            "current_working_directory": "/Users/janossch/dev/linux-configurations/.aws/amazonq",
            "environment_variables": []
          }
        },
        "content": {
          "Prompt": {
            "prompt": "In the current folder you will find the configuration files for Amazon Q CLI, I want to build a robust way to load the contexts, profiles and hooks into Amazon Q CLI, so I can share that with others. What would be your recommendation?"
          }
        },
        "images": null
      },
      {
        "ToolUse": {
          "message_id": "d1085099-5a5d-452c-a46e-970e20c68d4e",
          "content": "Let me first examine the current folder structure to understand your Amazon Q CLI configuration setup.",
          "tool_uses": [
            {
              "id": "tooluse_fWL6BQaVTHuE6rEJ3ZAHBQ",
              "name": "fs_read",
              "orig_name": "fs_read",
              "args": {
                "mode": "Directory",
                "path": "/Users/janossch/dev/linux-configurations/.aws/amazonq"
              },
              "orig_args": {
                "mode": "Directory",
                "path": "/Users/janossch/dev/linux-configurations/.aws/amazonq"
              }
            }
          ]
        }
      }
    ],
    [
      {
        "additional_context": "",
        "env_context": {
          "env_state": {
            "operating_system": "macos",
            "current_working_directory": "/Users/janossch/dev/linux-configurations/.aws/amazonq",
            "environment_variables": []
          }
        },
        "content": {
          "ToolUseResults": {
            "tool_use_results": [
              {
                "tool_use_id": "tooluse_fWL6BQaVTHuE6rEJ3ZAHBQ",
                "content": [
                  {
                    "Text": "-rw------- 1 2023233259 20 66 Jul 30 04:14 /Users/janossch/dev/linux-configurations/.aws/amazonq/active-user-state.json\ndrwxr-xr-x 16 2023233259 20 512 Dec 19 04:49 /Users/janossch/dev/linux-configurations/.aws/amazonq/cache\ndrwxr-xr-x 3 2023233259 20 96 Jul 24 04:19 /Users/janossch/dev/linux-configurations/.aws/amazonq/agents\n-rw-r--r-- 1 2023233259 20 2340 Jul 02 09:11 /Users/janossch/dev/linux-configurations/.aws/amazonq/mcp.json.bak\ndrwxr-xr-x 4 2023233259 20 128 Jul 30 03:56 /Users/janossch/dev/linux-configurations/.aws/amazonq/personas\n-rw------- 1 2023233259 20 235 May 16 05:26 /Users/janossch/dev/linux-configurations/.aws/amazonq/mcp.json.backup\ndrwxr-xr-x 5 2023233259 20 160 Jul 30 04:16 /Users/janossch/dev/linux-configurations/.aws/amazonq/hooks\ndrwxr-xr-x 55 2023233259 20 1760 Jul 30 03:54 /Users/janossch/dev/linux-configurations/.aws/amazonq/history\n-rw-r--r-- 1 2023233259 20 568406 Jul 30 04:13 /Users/janossch/dev/linux-configurations/.aws/amazonq/lspLog.log\n-rw-r--r-- 1 2023233259 20 148 May 18 09:54 /Users/janossch/dev/linux-configurations/.aws/amazonq/global_context.json\ndrwxr-xr-x 5 2023233259 20 160 May 18 09:54 /Users/janossch/dev/linux-configurations/.aws/amazonq/profiles\n-rw------- 1 2023233259 1896053708 2366 Jul 04 03:54 /Users/janossch/dev/linux-configurations/.aws/amazonq/mcp.json"
                  }
                ],
                "status": "Success"
              }
            ]
          }
        },
        "images": null
      },
      {
        "ToolUse": {
          "message_id": "20626844-772c-4768-901c-c4e85b2a26c7",
          "content": "Now let me examine the key configuration files to understand the structure:",
          "tool_uses": [
            {
              "id": "tooluse_ODyVAoo2RAaE5_21Okullg",
              "name": "fs_read",
              "orig_name": "fs_read",
              "args": {
                "mode": "Line",
                "path": "/Users/janossch/dev/linux-configurations/.aws/amazonq/mcp.json"
              },
              "orig_args": {
                "mode": "Line",
                "path": "/Users/janossch/dev/linux-configurations/.aws/amazonq/mcp.json"
              }
            }
          ]
        }
      }
    ],
    [
      {
        "additional_context": "",
        "env_context": {
          "env_state": {
            "operating_system": "macos",
            "current_working_directory": "/Users/janossch/dev/linux-configurations/.aws/amazonq",
            "environment_variables": []
          }
        },
        "content": {
          "ToolUseResults": {
            "tool_use_results": [
              {
                "tool_use_id": "tooluse_ODyVAoo2RAaE5_21Okullg",
                "content": [
                  {
                    "Text": "{\n  \"mcpServers\": {\n    \"aidlc\": {\n      \"command\": \"aidlc-mcp-sdk\",\n      \"args\": [\n        \"--debug\"\n      ],\n      \"env\": {}\n    },\n    \"amazon-internal-mcp-server\": {\n      \"command\": \"amzn-mcp\",\n      \"args\": [],\n      \"env\": {}\n    },\n    \"fetch\": {\n      \"command\": \"uvx\",\n      \"args\": [\n        \"mcp-server-fetch\"\n      ]\n    },\n    \"outlook-mcp-server\": {\n      \"command\": \"/Users/janossch/dev/OutlookForMac-mcp-server/outlook_mcp.py\",\n      \"args\": [],\n      \"env\": {\n        \"OUTLOOK_MCP_LOG_LEVEL\": \"DEBUG\",\n        \"USER_EMAIL\": \"janossch@amazon.com\",\n        \"PYTHON_PATH\": \"/Users/janossch/.pyenv/shims/python\"\n      },\n      \"disabled\": false \n    },\n    \"awslabs.core-mcp-server\": {\n      \"command\": \"uvx\",\n      \"args\": [\n        \"awslabs.core-mcp-server@latest\"\n      ],\n      \"env\": {\n        \"FASTMCP_LOG_LEVEL\": \"ERROR\"\n      },\n      \"autoApprove\": [],\n      \"disabled\": false\n    },\n    \"awslabs.aws-documentation-mcp-server\": {\n      \"command\": \"uvx\",\n      \"args\": [\n        \"awslabs.aws-documentation-mcp-server@latest\"\n      ],\n      \"env\": {\n        \"FASTMCP_LOG_LEVEL\": \"ERROR\"\n      },\n      \"disabled\": false,\n      \"autoApprove\": []\n    },\n    \"awslabs.cdk-mcp-server\": {\n      \"command\": \"uvx\",\n      \"args\": [\n        \"awslabs.cdk-mcp-server@latest\"\n      ],\n      \"env\": {\n        \"FASTMCP_LOG_LEVEL\": \"ERROR\"\n      },\n      \"disabled\": false,\n      \"autoApprove\": []\n    },\n    \"awslabs.terraform-mcp-server\": {\n      \"command\": \"uvx\",\n      \"args\": [\n        \"awslabs.terraform-mcp-server@latest\"\n      ],\n      \"env\": {\n        \"FASTMCP_LOG_LEVEL\": \"ERROR\"\n      },\n      \"disabled\": true,\n      \"autoApprove\": []\n    },\n    \"awslabs.aws-diagram-mcp-server\": {\n      \"command\": \"uvx\",\n      \"args\": [\n        \"awslabs.aws-diagram-mcp-server\"\n      ],\n      \"env\": {\n        \"FASTMCP_LOG_LEVEL\": \"ERROR\"\n      },\n      \"autoApprove\": [],\n      \"disabled\": false\n    },\n    \"aws-cloudhsm-migration-tool\": {\n      \"command\": \"/Users/janossch/dev/aidlc/aws-cloudhsm-migration-tool/aws-cloudhsm-migration-tool-production/cloudhsm_migration_mcp_server.py\",\n      \"args\": [],\n      \"env\": {\n        \"FASTMCP_LOG_LEVEL\": \"INFO\",\n        \"CLOUDHSM_MIGRATION_TOOL_HOME\": \"/Users/janossch/dev/aidlc/aws-cloudhsm-migration-tool/aws-cloudhsm-migration-tool-production\"\n      },\n      \"autoApprove\": [],\n      \"disabled\": false\n    }\n  }\n}"
                  }
                ],
                "status": "Success"
              }
            ]
          }
        },
        "images": null
      },
      {
        "ToolUse": {
          "message_id": "b81a140a-d547-412a-9bfb-d6b3127bd8bd",
          "content": "",
          "tool_uses": [
            {
              "id": "tooluse_O2ky6xo3SeKWqdfX6Budzw",
              "name": "fs_read",
              "orig_name": "fs_read",
              "args": {
                "mode": "Directory",
                "path": "/Users/janossch/dev/linux-configurations/.aws/amazonq/profiles"
              },
              "orig_args": {
                "mode": "Directory",
                "path": "/Users/janossch/dev/linux-configurations/.aws/amazonq/profiles"
              }
            }
          ]
        }
      }
    ],
    [
      {
        "additional_context": "",
        "env_context": {
          "env_state": {
            "operating_system": "macos",
            "current_working_directory": "/Users/janossch/dev/linux-configurations/.aws/amazonq",
            "environment_variables": []
          }
        },
        "content": {
          "ToolUseResults": {
            "tool_use_results": [
              {
                "tool_use_id": "tooluse_O2ky6xo3SeKWqdfX6Budzw",
                "content": [
                  {
                    "Text": "drwxr-xr-x 3 2023233259 20 96 May 13 00:31 /Users/janossch/dev/linux-configurations/.aws/amazonq/profiles/discovery\ndrwxr-xr-x 3 2023233259 20 96 Apr 11 03:05 /Users/janossch/dev/linux-configurations/.aws/amazonq/profiles/default\ndrwxr-xr-x 3 2023233259 20 96 May 18 09:54 /Users/janossch/dev/linux-configurations/.aws/amazonq/profiles/solutions_space"
                  }
                ],
                "status": "Success"
              }
            ]
          }
        },
        "images": null
      },
      {
        "ToolUse": {
          "message_id": "0b41cca8-5b3d-4133-bf93-60d2db9ea234",
          "content": "",
          "tool_uses": [
            {
              "id": "tooluse_XPkWycPPQG2XgYC3bfkmyg",
              "name": "fs_read",
              "orig_name": "fs_read",
              "args": {
                "mode": "Directory",
                "path": "/Users/janossch/dev/linux-configurations/.aws/amazonq/hooks"
              },
              "orig_args": {
                "mode": "Directory",
                "path": "/Users/janossch/dev/linux-configurations/.aws/amazonq/hooks"
              }
            }
          ]
        }
      }
    ],
    [
      {
        "additional_context": "",
        "env_context": {
          "env_state": {
            "operating_system": "macos",
            "current_working_directory": "/Users/janossch/dev/linux-configurations/.aws/amazonq",
            "environment_variables": []
          }
        },
        "content": {
          "ToolUseResults": {
            "tool_use_results": [
              {
                "tool_use_id": "tooluse_XPkWycPPQG2XgYC3bfkmyg",
                "content": [
                  {
                    "Text": "-rw-r--r-- 1 2023233259 20 134 Jul 30 04:14 /Users/janossch/dev/linux-configurations/.aws/amazonq/hooks/ai_hooks.sh\n-rw-r--r-- 1 2023233259 20 142 Jul 30 04:15 /Users/janossch/dev/linux-configurations/.aws/amazonq/hooks/config.yaml\n-rw-r--r-- 1 2023233259 20 695 Jul 30 04:16 /Users/janossch/dev/linux-configurations/.aws/amazonq/hooks/ai_hooks.py"
                  }
                ],
                "status": "Success"
              }
            ]
          }
        },
        "images": null
      },
      {
        "ToolUse": {
          "message_id": "b286ae2f-6afb-467b-97a2-ccfb164e8815",
          "content": "Let me examine the profiles and hooks structure:",
          "tool_uses": [
            {
              "id": "tooluse_zOi0xwlZQi2iFZwpoJw6tQ",
              "name": "fs_read",
              "orig_name": "fs_read",
              "args": {
                "mode": "Line",
                "path": "/Users/janossch/dev/linux-configurations/.aws/amazonq/profiles/default",
                "depth": 2
              },
              "orig_args": {
                "mode": "Line",
                "path": "/Users/janossch/dev/linux-configurations/.aws/amazonq/profiles/default",
                "depth": 2
              }
            }
          ]
        }
      }
    ],
    [
      {
        "additional_context": "",
        "env_context": {
          "env_state": {
            "operating_system": "macos",
            "current_working_directory": "/Users/janossch/dev/linux-configurations/.aws/amazonq",
            "environment_variables": []
          }
        },
        "content": {
          "ToolUseResults": {
            "tool_use_results": [
              {
                "tool_use_id": "tooluse_zOi0xwlZQi2iFZwpoJw6tQ",
                "content": [
                  {
                    "Text": "Failed to validate tool parameters: '/Users/janossch/dev/linux-configurations/.aws/amazonq/profiles/default' is not a file"
                  }
                ],
                "status": "Error"
              }
            ]
          }
        },
        "images": null
      },
      {
        "ToolUse": {
          "message_id": "cec3b6ea-ab31-4469-8bc1-3b1d275fa72d",
          "content": "",
          "tool_uses": [
            {
              "id": "tooluse_C-3PU8zSTMylEavyEMQAUQ",
              "name": "fs_read",
              "orig_name": "fs_read",
              "args": {
                "mode": "Directory",
                "path": "/Users/janossch/dev/linux-configurations/.aws/amazonq/profiles/default",
                "depth": 2
              },
              "orig_args": {
                "mode": "Directory",
                "path": "/Users/janossch/dev/linux-configurations/.aws/amazonq/profiles/default",
                "depth": 2
              }
            }
          ]
        }
      }
    ],
    [
      {
        "additional_context": "",
        "env_context": {
          "env_state": {
            "operating_system": "macos",
            "current_working_directory": "/Users/janossch/dev/linux-configurations/.aws/amazonq",
            "environment_variables": []
          }
        },
        "content": {
          "ToolUseResults": {
            "tool_use_results": [
              {
                "tool_use_id": "tooluse_C-3PU8zSTMylEavyEMQAUQ",
                "content": [
                  {
                    "Text": "-rw-r--r-- 1 2023233259 20 17 Apr 15 05:55 /Users/janossch/dev/linux-configurations/.aws/amazonq/profiles/default/context.json"
                  }
                ],
                "status": "Success"
              }
            ]
          }
        },
        "images": null
      },
      {
        "ToolUse": {
          "message_id": "ed6822ed-f5f0-41fb-b1fe-49eedb6a326d",
          "content": "",
          "tool_uses": [
            {
              "id": "tooluse_ftmSryRBQEC7evkDrz-5yQ",
              "name": "fs_read",
              "orig_name": "fs_read",
              "args": {
                "mode": "Line",
                "path": "/Users/janossch/dev/linux-configurations/.aws/amazonq/profiles/default/context.json"
              },
              "orig_args": {
                "mode": "Line",
                "path": "/Users/janossch/dev/linux-configurations/.aws/amazonq/profiles/default/context.json"
              }
            }
          ]
        }
      }
    ],
    [
      {
        "additional_context": "",
        "env_context": {
          "env_state": {
            "operating_system": "macos",
            "current_working_directory": "/Users/janossch/dev/linux-configurations/.aws/amazonq",
            "environment_variables": []
          }
        },
        "content": {
          "ToolUseResults": {
            "tool_use_results": [
              {
                "tool_use_id": "tooluse_ftmSryRBQEC7evkDrz-5yQ",
                "content": [
                  {
                    "Text": "{\n  \"paths\": []\n}"
                  }
                ],
                "status": "Success"
              }
            ]
          }
        },
        "images": null
      },
      {
        "ToolUse": {
          "message_id": "78f0ca1d-aa78-4367-b76b-3c10c531595c",
          "content": "",
          "tool_uses": [
            {
              "id": "tooluse_aJPBBdRDQ-WlaIgr1wMa3Q",
              "name": "fs_read",
              "orig_name": "fs_read",
              "args": {
                "mode": "Line",
                "path": "/Users/janossch/dev/linux-configurations/.aws/amazonq/hooks/config.yaml"
              },
              "orig_args": {
                "mode": "Line",
                "path": "/Users/janossch/dev/linux-configurations/.aws/amazonq/hooks/config.yaml"
              }
            }
          ]
        }
      }
    ],
    [
      {
        "additional_context": "",
        "env_context": {
          "env_state": {
            "operating_system": "macos",
            "current_working_directory": "/Users/janossch/dev/linux-configurations/.aws/amazonq",
            "environment_variables": []
          }
        },
        "content": {
          "ToolUseResults": {
            "tool_use_results": [
              {
                "tool_use_id": "tooluse_aJPBBdRDQ-WlaIgr1wMa3Q",
                "content": [
                  {
                    "Text": "contexts:\n  default:\n    - \"context.txt\"\n  dev:\n    - \"dev_context.txt\"\n    - \"common.txt\"\n  prod:\n    - \"prod_context.txt\"\n    - \"common.txt\""
                  }
                ],
                "status": "Success"
              }
            ]
          }
        },
        "images": null
      },
      {
        "ToolUse": {
          "message_id": "e0e80c9e-a585-4ce1-a1c3-c90a79abc9a0",
          "content": "",
          "tool_uses": [
            {
              "id": "tooluse_kkW6DtUeRI6jCJE84BXMgg",
              "name": "fs_read",
              "orig_name": "fs_read",
              "args": {
                "mode": "Line",
                "path": "/Users/janossch/dev/linux-configurations/.aws/amazonq/hooks/ai_hooks.py"
              },
              "orig_args": {
                "mode": "Line",
                "path": "/Users/janossch/dev/linux-configurations/.aws/amazonq/hooks/ai_hooks.py"
              }
            }
          ]
        }
      }
    ],
    [
      {
        "additional_context": "",
        "env_context": {
          "env_state": {
            "operating_system": "macos",
            "current_working_directory": "/Users/janossch/dev/linux-configurations/.aws/amazonq",
            "environment_variables": []
          }
        },
        "content": {
          "ToolUseResults": {
            "tool_use_results": [
              {
                "tool_use_id": "tooluse_kkW6DtUeRI6jCJE84BXMgg",
                "content": [
                  {
                    "Text": "#!/usr/bin/env python3\nimport sys\nimport yaml\nfrom pathlib import Path\n\ndef load_context(context_name):\n    config_path = Path(__file__).parent / \"config.yaml\"\n    \n    with open(config_path) as f:\n        config = yaml.safe_load(f)\n    \n    files = config[\"contexts\"].get(context_name, [context_name])\n    \n    for file_name in files:\n        file_path = Path(file_name)\n        if file_path.exists():\n            print(file_path.read_text(), end=\"\")\n        else:\n            print(f\"File '{file_name}' not found\", file=sys.stderr)\n\nif __name__ == \"__main__\":\n    if len(sys.argv) < 2:\n        print(\"Usage: python ai_hooks.py <context>\")\n        sys.exit(1)\n    \n    load_context(sys.argv[1])"
                  }
                ],
                "status": "Success"
              }
            ]
          }
        },
        "images": null
      },
      {
        "ToolUse": {
          "message_id": "f8383200-7c7f-40a2-b10a-116d3baf79c7",
          "content": "",
          "tool_uses": [
            {
              "id": "tooluse_mO9zQTyAT02SVgT6VPYkzQ",
              "name": "fs_read",
              "orig_name": "fs_read",
              "args": {
                "mode": "Line",
                "path": "/Users/janossch/dev/linux-configurations/.aws/amazonq/global_context.json"
              },
              "orig_args": {
                "mode": "Line",
                "path": "/Users/janossch/dev/linux-configurations/.aws/amazonq/global_context.json"
              }
            }
          ]
        }
      }
    ],
    [
      {
        "additional_context": "",
        "env_context": {
          "env_state": {
            "operating_system": "macos",
            "current_working_directory": "/Users/janossch/dev/linux-configurations/.aws/amazonq",
            "environment_variables": []
          }
        },
        "content": {
          "ToolUseResults": {
            "tool_use_results": [
              {
                "tool_use_id": "tooluse_mO9zQTyAT02SVgT6VPYkzQ",
                "content": [
                  {
                    "Text": "{\n  \"paths\": [\n    \".amazonq/rules/**/*.md\",\n    \"README.md\",\n    \"AmazonQ.md\",\n    \"/Users/janossch/.aidlc/contexts/common.md\"\n  ],\n  \"hooks\": {}\n}"
                  }
                ],
                "status": "Success"
              }
            ]
          }
        },
        "images": null
      },
      {
        "ToolUse": {
          "message_id": "72a33684-5954-4b7c-82c9-c46e6c6f50c1",
          "content": "Based on my analysis of your Amazon Q CLI configuration, here's my recommendation for building a robust, shareable configuration system:\n\n## Recommended Approach: Configuration as Code with Setup Scripts\n\n### 1. Create a Structured Repository Layout\n\n```\namazonq-config/\n├── README.md\n├── setup.sh                    # Main setup script\n├── config/\n│   ├── mcp.json               # MCP server configurations\n│   ├── global_context.json   # Global context paths\n│   └── profiles/              # Profile configurations\n│       ├── default/\n│       ├── development/\n│       └── production/\n├── contexts/                  # Shared context files\n│   ├── common.md\n│   ├── aws-best-practices.md\n│   └── project-specific/\n├── hooks/                     # Hook scripts and configs\n│   ├── config.yaml\n│   ├── ai_hooks.py\n│   └── ai_hooks.sh\n└── scripts/\n    ├── install-dependencies.sh\n    ├── validate-config.sh\n    └── backup-existing.sh\n```\n\n### 2. Create a Smart Setup Script",
          "tool_uses": [
            {
              "id": "tooluse_oP8SoA0KRrG4xwrZBoursg",
              "name": "fs_write",
              "orig_name": "fs_write",
              "args": {
                "command": "create",
                "path": "/Users/janossch/dev/linux-configurations/.aws/amazonq/setup-amazonq-config.sh",
                "file_text": "#!/bin/bash\n\n# Amazon Q CLI Configuration Setup Script\n# This script helps set up a robust, shareable Amazon Q CLI configuration\n\nset -e\n\n# Colors for output\nRED='\\033[0;31m'\nGREEN='\\033[0;32m'\nYELLOW='\\033[1;33m'\nBLUE='\\033[0;34m'\nNC='\\033[0m' # No Color\n\n# Configuration\nAMAZONQ_DIR=\"$HOME/.aws/amazonq\"\nBACKUP_DIR=\"$HOME/.aws/amazonq-backup-$(date +%Y%m%d-%H%M%S)\"\nCONFIG_REPO_URL=\"${1:-}\"\n\nprint_status() {\n    echo -e \"${BLUE}[INFO]${NC} $1\"\n}\n\nprint_success() {\n    echo -e \"${GREEN}[SUCCESS]${NC} $1\"\n}\n\nprint_warning() {\n    echo -e \"${YELLOW}[WARNING]${NC} $1\"\n}\n\nprint_error() {\n    echo -e \"${RED}[ERROR]${NC} $1\"\n}\n\n# Function to backup existing configuration\nbackup_existing_config() {\n    if [ -d \"$AMAZONQ_DIR\" ]; then\n        print_status \"Backing up existing configuration to $BACKUP_DIR\"\n        cp -r \"$AMAZONQ_DIR\" \"$BACKUP_DIR\"\n        print_success \"Backup completed\"\n    fi\n}\n\n# Function to validate dependencies\ncheck_dependencies() {\n    print_status \"Checking dependencies...\"\n    \n    local missing_deps=()\n    \n    # Check for required tools\n    command -v python3 >/dev/null 2>&1 || missing_deps+=(\"python3\")\n    command -v uvx >/dev/null 2>&1 || missing_deps+=(\"uvx\")\n    command -v q >/dev/null 2>&1 || missing_deps+=(\"amazon-q-cli\")\n    \n    if [ ${#missing_deps[@]} -ne 0 ]; then\n        print_error \"Missing dependencies: ${missing_deps[*]}\"\n        print_status \"Please install missing dependencies and run again\"\n        exit 1\n    fi\n    \n    print_success \"All dependencies found\"\n}\n\n# Function to install Python dependencies\ninstall_python_deps() {\n    print_status \"Installing Python dependencies...\"\n    pip3 install --user pyyaml\n    print_success \"Python dependencies installed\"\n}\n\n# Function to setup directory structure\nsetup_directories() {\n    print_status \"Setting up directory structure...\"\n    \n    mkdir -p \"$AMAZONQ_DIR\"/{profiles,hooks,contexts,cache,history}\n    mkdir -p \"$AMAZONQ_DIR/profiles\"/{default,development,production}\n    \n    print_success \"Directory structure created\"\n}\n\n# Function to copy configuration files\ncopy_configs() {\n    local source_dir=\"$1\"\n    \n    if [ -z \"$source_dir\" ] || [ ! -d \"$source_dir\" ]; then\n        print_warning \"No source directory provided or directory doesn't exist\"\n        print_status \"Creating default configuration...\"\n        create_default_config\n        return\n    fi\n    \n    print_status \"Copying configuration files from $source_dir\"\n    \n    # Copy MCP configuration\n    if [ -f \"$source_dir/config/mcp.json\" ]; then\n        cp \"$source_dir/config/mcp.json\" \"$AMAZONQ_DIR/mcp.json\"\n    fi\n    \n    # Copy global context\n    if [ -f \"$source_dir/config/global_context.json\" ]; then\n        cp \"$source_dir/config/global_context.json\" \"$AMAZONQ_DIR/global_context.json\"\n    fi\n    \n    # Copy profiles\n    if [ -d \"$source_dir/config/profiles\" ]; then\n        cp -r \"$source_dir/config/profiles\"/* \"$AMAZONQ_DIR/profiles/\"\n    fi\n    \n    # Copy hooks\n    if [ -d \"$source_dir/hooks\" ]; then\n        cp -r \"$source_dir/hooks\"/* \"$AMAZONQ_DIR/hooks/\"\n    fi\n    \n    # Copy contexts\n    if [ -d \"$source_dir/contexts\" ]; then\n        cp -r \"$source_dir/contexts\"/* \"$AMAZONQ_DIR/contexts/\"\n    fi\n    \n    print_success \"Configuration files copied\"\n}\n\n# Function to create default configuration\ncreate_default_config() {\n    print_status \"Creating default configuration files...\"\n    \n    # Create default MCP configuration\n    cat > \"$AMAZONQ_DIR/mcp.json\" << 'EOF'\n{\n  \"mcpServers\": {\n    \"fetch\": {\n      \"command\": \"uvx\",\n      \"args\": [\"mcp-server-fetch\"]\n    },\n    \"awslabs.core-mcp-server\": {\n      \"command\": \"uvx\",\n      \"args\": [\"awslabs.core-mcp-server@latest\"],\n      \"env\": {\n        \"FASTMCP_LOG_LEVEL\": \"ERROR\"\n      },\n      \"autoApprove\": [],\n      \"disabled\": false\n    }\n  }\n}\nEOF\n    \n    # Create default global context\n    cat > \"$AMAZONQ_DIR/global_context.json\" << 'EOF'\n{\n  \"paths\": [\n    \".amazonq/rules/**/*.md\",\n    \"README.md\"\n  ],\n  \"hooks\": {}\n}\nEOF\n    \n    # Create default profile\n    cat > \"$AMAZONQ_DIR/profiles/default/context.json\" << 'EOF'\n{\n  \"paths\": []\n}\nEOF\n    \n    print_success \"Default configuration created\"\n}\n\n# Function to set permissions\nset_permissions() {\n    print_status \"Setting appropriate permissions...\"\n    \n    # Set restrictive permissions for sensitive files\n    chmod 600 \"$AMAZONQ_DIR/mcp.json\" 2>/dev/null || true\n    chmod 600 \"$AMAZONQ_DIR\"/*.json 2>/dev/null || true\n    \n    # Make hook scripts executable\n    chmod +x \"$AMAZONQ_DIR/hooks\"/*.sh 2>/dev/null || true\n    chmod +x \"$AMAZONQ_DIR/hooks\"/*.py 2>/dev/null || true\n    \n    print_success \"Permissions set\"\n}\n\n# Function to validate configuration\nvalidate_config() {\n    print_status \"Validating configuration...\"\n    \n    # Check if MCP configuration is valid JSON\n    if ! python3 -m json.tool \"$AMAZONQ_DIR/mcp.json\" >/dev/null 2>&1; then\n        print_error \"Invalid MCP configuration JSON\"\n        return 1\n    fi\n    \n    # Check if global context is valid JSON\n    if ! python3 -m json.tool \"$AMAZONQ_DIR/global_context.json\" >/dev/null 2>&1; then\n        print_error \"Invalid global context JSON\"\n        return 1\n    fi\n    \n    print_success \"Configuration validation passed\"\n}\n\n# Function to test MCP servers\ntest_mcp_servers() {\n    print_status \"Testing MCP server connections...\"\n    print_warning \"This may take a moment as servers are initialized...\"\n    \n    # Test with a simple Q command\n    if q --help >/dev/null 2>&1; then\n        print_success \"Amazon Q CLI is working\"\n    else\n        print_warning \"Amazon Q CLI test failed - please check your installation\"\n    fi\n}\n\n# Main setup function\nmain() {\n    echo -e \"${BLUE}Amazon Q CLI Configuration Setup${NC}\"\n    echo \"==================================\"\n    echo\n    \n    # Parse arguments\n    local source_dir=\"\"\n    if [ -n \"$CONFIG_REPO_URL\" ]; then\n        if [ -d \"$CONFIG_REPO_URL\" ]; then\n            source_dir=\"$CONFIG_REPO_URL\"\n        else\n            print_error \"Provided path is not a directory: $CONFIG_REPO_URL\"\n            exit 1\n        fi\n    fi\n    \n    # Run setup steps\n    check_dependencies\n    backup_existing_config\n    install_python_deps\n    setup_directories\n    copy_configs \"$source_dir\"\n    set_permissions\n    validate_config\n    test_mcp_servers\n    \n    echo\n    print_success \"Amazon Q CLI configuration setup completed!\"\n    echo\n    echo -e \"${BLUE}Next steps:${NC}\"\n    echo \"1. Test your configuration: q chat\"\n    echo \"2. Customize profiles in: $AMAZONQ_DIR/profiles/\"\n    echo \"3. Add context files in: $AMAZONQ_DIR/contexts/\"\n    echo \"4. Modify MCP servers in: $AMAZONQ_DIR/mcp.json\"\n    echo\n    if [ -d \"$BACKUP_DIR\" ]; then\n        echo -e \"${YELLOW}Your previous configuration was backed up to:${NC}\"\n        echo \"$BACKUP_DIR\"\n    fi\n}\n\n# Show usage if help requested\nif [ \"$1\" = \"--help\" ] || [ \"$1\" = \"-h\" ]; then\n    echo \"Usage: $0 [CONFIG_SOURCE_DIR]\"\n    echo\n    echo \"Setup Amazon Q CLI configuration from a source directory or create default config.\"\n    echo\n    echo \"Arguments:\"\n    echo \"  CONFIG_SOURCE_DIR  Path to directory containing configuration files\"\n    echo\n    echo \"Options:\"\n    echo \"  -h, --help        Show this help message\"\n    echo\n    echo \"Examples:\"\n    echo \"  $0                           # Create default configuration\"\n    echo \"  $0 ./my-amazonq-config       # Use configuration from directory\"\n    exit 0\nfi\n\n# Run main function\nmain \"$@\"",
                "summary": "Create a comprehensive setup script for Amazon Q CLI configuration"
              },
              "orig_args": {
                "command": "create",
                "path": "/Users/janossch/dev/linux-configurations/.aws/amazonq/setup-amazonq-config.sh",
                "file_text": "#!/bin/bash\n\n# Amazon Q CLI Configuration Setup Script\n# This script helps set up a robust, shareable Amazon Q CLI configuration\n\nset -e\n\n# Colors for output\nRED='\\033[0;31m'\nGREEN='\\033[0;32m'\nYELLOW='\\033[1;33m'\nBLUE='\\033[0;34m'\nNC='\\033[0m' # No Color\n\n# Configuration\nAMAZONQ_DIR=\"$HOME/.aws/amazonq\"\nBACKUP_DIR=\"$HOME/.aws/amazonq-backup-$(date +%Y%m%d-%H%M%S)\"\nCONFIG_REPO_URL=\"${1:-}\"\n\nprint_status() {\n    echo -e \"${BLUE}[INFO]${NC} $1\"\n}\n\nprint_success() {\n    echo -e \"${GREEN}[SUCCESS]${NC} $1\"\n}\n\nprint_warning() {\n    echo -e \"${YELLOW}[WARNING]${NC} $1\"\n}\n\nprint_error() {\n    echo -e \"${RED}[ERROR]${NC} $1\"\n}\n\n# Function to backup existing configuration\nbackup_existing_config() {\n    if [ -d \"$AMAZONQ_DIR\" ]; then\n        print_status \"Backing up existing configuration to $BACKUP_DIR\"\n        cp -r \"$AMAZONQ_DIR\" \"$BACKUP_DIR\"\n        print_success \"Backup completed\"\n    fi\n}\n\n# Function to validate dependencies\ncheck_dependencies() {\n    print_status \"Checking dependencies...\"\n    \n    local missing_deps=()\n    \n    # Check for required tools\n    command -v python3 >/dev/null 2>&1 || missing_deps+=(\"python3\")\n    command -v uvx >/dev/null 2>&1 || missing_deps+=(\"uvx\")\n    command -v q >/dev/null 2>&1 || missing_deps+=(\"amazon-q-cli\")\n    \n    if [ ${#missing_deps[@]} -ne 0 ]; then\n        print_error \"Missing dependencies: ${missing_deps[*]}\"\n        print_status \"Please install missing dependencies and run again\"\n        exit 1\n    fi\n    \n    print_success \"All dependencies found\"\n}\n\n# Function to install Python dependencies\ninstall_python_deps() {\n    print_status \"Installing Python dependencies...\"\n    pip3 install --user pyyaml\n    print_success \"Python dependencies installed\"\n}\n\n# Function to setup directory structure\nsetup_directories() {\n    print_status \"Setting up directory structure...\"\n    \n    mkdir -p \"$AMAZONQ_DIR\"/{profiles,hooks,contexts,cache,history}\n    mkdir -p \"$AMAZONQ_DIR/profiles\"/{default,development,production}\n    \n    print_success \"Directory structure created\"\n}\n\n# Function to copy configuration files\ncopy_configs() {\n    local source_dir=\"$1\"\n    \n    if [ -z \"$source_dir\" ] || [ ! -d \"$source_dir\" ]; then\n        print_warning \"No source directory provided or directory doesn't exist\"\n        print_status \"Creating default configuration...\"\n        create_default_config\n        return\n    fi\n    \n    print_status \"Copying configuration files from $source_dir\"\n    \n    # Copy MCP configuration\n    if [ -f \"$source_dir/config/mcp.json\" ]; then\n        cp \"$source_dir/config/mcp.json\" \"$AMAZONQ_DIR/mcp.json\"\n    fi\n    \n    # Copy global context\n    if [ -f \"$source_dir/config/global_context.json\" ]; then\n        cp \"$source_dir/config/global_context.json\" \"$AMAZONQ_DIR/global_context.json\"\n    fi\n    \n    # Copy profiles\n    if [ -d \"$source_dir/config/profiles\" ]; then\n        cp -r \"$source_dir/config/profiles\"/* \"$AMAZONQ_DIR/profiles/\"\n    fi\n    \n    # Copy hooks\n    if [ -d \"$source_dir/hooks\" ]; then\n        cp -r \"$source_dir/hooks\"/* \"$AMAZONQ_DIR/hooks/\"\n    fi\n    \n    # Copy contexts\n    if [ -d \"$source_dir/contexts\" ]; then\n        cp -r \"$source_dir/contexts\"/* \"$AMAZONQ_DIR/contexts/\"\n    fi\n    \n    print_success \"Configuration files copied\"\n}\n\n# Function to create default configuration\ncreate_default_config() {\n    print_status \"Creating default configuration files...\"\n    \n    # Create default MCP configuration\n    cat > \"$AMAZONQ_DIR/mcp.json\" << 'EOF'\n{\n  \"mcpServers\": {\n    \"fetch\": {\n      \"command\": \"uvx\",\n      \"args\": [\"mcp-server-fetch\"]\n    },\n    \"awslabs.core-mcp-server\": {\n      \"command\": \"uvx\",\n      \"args\": [\"awslabs.core-mcp-server@latest\"],\n      \"env\": {\n        \"FASTMCP_LOG_LEVEL\": \"ERROR\"\n      },\n      \"autoApprove\": [],\n      \"disabled\": false\n    }\n  }\n}\nEOF\n    \n    # Create default global context\n    cat > \"$AMAZONQ_DIR/global_context.json\" << 'EOF'\n{\n  \"paths\": [\n    \".amazonq/rules/**/*.md\",\n    \"README.md\"\n  ],\n  \"hooks\": {}\n}\nEOF\n    \n    # Create default profile\n    cat > \"$AMAZONQ_DIR/profiles/default/context.json\" << 'EOF'\n{\n  \"paths\": []\n}\nEOF\n    \n    print_success \"Default configuration created\"\n}\n\n# Function to set permissions\nset_permissions() {\n    print_status \"Setting appropriate permissions...\"\n    \n    # Set restrictive permissions for sensitive files\n    chmod 600 \"$AMAZONQ_DIR/mcp.json\" 2>/dev/null || true\n    chmod 600 \"$AMAZONQ_DIR\"/*.json 2>/dev/null || true\n    \n    # Make hook scripts executable\n    chmod +x \"$AMAZONQ_DIR/hooks\"/*.sh 2>/dev/null || true\n    chmod +x \"$AMAZONQ_DIR/hooks\"/*.py 2>/dev/null || true\n    \n    print_success \"Permissions set\"\n}\n\n# Function to validate configuration\nvalidate_config() {\n    print_status \"Validating configuration...\"\n    \n    # Check if MCP configuration is valid JSON\n    if ! python3 -m json.tool \"$AMAZONQ_DIR/mcp.json\" >/dev/null 2>&1; then\n        print_error \"Invalid MCP configuration JSON\"\n        return 1\n    fi\n    \n    # Check if global context is valid JSON\n    if ! python3 -m json.tool \"$AMAZONQ_DIR/global_context.json\" >/dev/null 2>&1; then\n        print_error \"Invalid global context JSON\"\n        return 1\n    fi\n    \n    print_success \"Configuration validation passed\"\n}\n\n# Function to test MCP servers\ntest_mcp_servers() {\n    print_status \"Testing MCP server connections...\"\n    print_warning \"This may take a moment as servers are initialized...\"\n    \n    # Test with a simple Q command\n    if q --help >/dev/null 2>&1; then\n        print_success \"Amazon Q CLI is working\"\n    else\n        print_warning \"Amazon Q CLI test failed - please check your installation\"\n    fi\n}\n\n# Main setup function\nmain() {\n    echo -e \"${BLUE}Amazon Q CLI Configuration Setup${NC}\"\n    echo \"==================================\"\n    echo\n    \n    # Parse arguments\n    local source_dir=\"\"\n    if [ -n \"$CONFIG_REPO_URL\" ]; then\n        if [ -d \"$CONFIG_REPO_URL\" ]; then\n            source_dir=\"$CONFIG_REPO_URL\"\n        else\n            print_error \"Provided path is not a directory: $CONFIG_REPO_URL\"\n            exit 1\n        fi\n    fi\n    \n    # Run setup steps\n    check_dependencies\n    backup_existing_config\n    install_python_deps\n    setup_directories\n    copy_configs \"$source_dir\"\n    set_permissions\n    validate_config\n    test_mcp_servers\n    \n    echo\n    print_success \"Amazon Q CLI configuration setup completed!\"\n    echo\n    echo -e \"${BLUE}Next steps:${NC}\"\n    echo \"1. Test your configuration: q chat\"\n    echo \"2. Customize profiles in: $AMAZONQ_DIR/profiles/\"\n    echo \"3. Add context files in: $AMAZONQ_DIR/contexts/\"\n    echo \"4. Modify MCP servers in: $AMAZONQ_DIR/mcp.json\"\n    echo\n    if [ -d \"$BACKUP_DIR\" ]; then\n        echo -e \"${YELLOW}Your previous configuration was backed up to:${NC}\"\n        echo \"$BACKUP_DIR\"\n    fi\n}\n\n# Show usage if help requested\nif [ \"$1\" = \"--help\" ] || [ \"$1\" = \"-h\" ]; then\n    echo \"Usage: $0 [CONFIG_SOURCE_DIR]\"\n    echo\n    echo \"Setup Amazon Q CLI configuration from a source directory or create default config.\"\n    echo\n    echo \"Arguments:\"\n    echo \"  CONFIG_SOURCE_DIR  Path to directory containing configuration files\"\n    echo\n    echo \"Options:\"\n    echo \"  -h, --help        Show this help message\"\n    echo\n    echo \"Examples:\"\n    echo \"  $0                           # Create default configuration\"\n    echo \"  $0 ./my-amazonq-config       # Use configuration from directory\"\n    exit 0\nfi\n\n# Run main function\nmain \"$@\"",
                "summary": "Create a comprehensive setup script for Amazon Q CLI configuration"
              }
            }
          ]
        }
      }
    ],
    [
      {
        "additional_context": "",
        "env_context": {
          "env_state": {
            "operating_system": "macos",
            "current_working_directory": "/Users/janossch/dev/linux-configurations/.aws/amazonq",
            "environment_variables": []
          }
        },
        "content": {
          "CancelledToolUses": {
            "prompt": "wait, let's do planning first, before implementation. I'm thinking more like some context, profiles and hooks repo with an installer, what do you think?",
            "tool_use_results": [
              {
                "tool_use_id": "tooluse_oP8SoA0KRrG4xwrZBoursg",
                "content": [
                  {
                    "Text": "Tool use was cancelled by the user"
                  }
                ],
                "status": "Error"
              }
            ]
          }
        },
        "images": null
      },
      {
        "Response": {
          "message_id": "d695854b-4efe-4581-968e-f56311635fc2",
          "content": "You're absolutely right - let's think through the planning first. Based on your current setup, I can see you have a sophisticated configuration with MCP servers, profiles, hooks, and contexts. Here's my strategic recommendation:\n\n## Planning: Amazon Q CLI Configuration Distribution System\n\n### **Core Concept: Modular Configuration Repository**\n\nCreate a repository structure that separates concerns and allows for easy customization:\n\n```\namazonq-shared-config/\n├── README.md\n├── install.sh                 # One-command installer\n├── configs/\n│   ├── mcp-servers/           # Modular MCP server definitions\n│   │   ├── core.json         # Essential servers (fetch, aws-core)\n│   │   ├── development.json  # Dev tools (outlook, internal tools)\n│   │   └── specialized.json  # Domain-specific (cloudhsm, diagrams)\n│   └── profiles/             # Pre-built profiles\n│       ├── aws-developer/\n│       ├── solutions-architect/\n│       └── enterprise-admin/\n├── contexts/                  # Shared knowledge base\n│   ├── aws-best-practices.md\n│   ├── security-guidelines.md\n│   └── troubleshooting.md\n├── hooks/                     # Automation scripts\n│   ├── context-loader.py\n│   └── profile-switcher.sh\n└── templates/                 # Customizable templates\n    ├── mcp-template.json\n    └── profile-template.json\n```\n\n### **Key Design Principles:**\n\n1. **Modularity**: Users can pick and choose components\n2. **Layered Configuration**: Base → Role-specific → Personal customizations\n3. **Version Control Friendly**: All configs in plain text/JSON\n4. **Environment Agnostic**: Works across different setups\n5. **Backward Compatible**: Preserves existing configurations\n\n### **Installation Strategy:**\n\n```bash\n# Simple one-liner installation\ncurl -sSL https://raw.githubusercontent.com/your-org/amazonq-config/main/install.sh | bash\n\n# Or with customization\n./install.sh --profile=solutions-architect --mcp=core,development\n```\n\n### **Configuration Layers:**\n\n1. **Base Layer**: Essential MCP servers (fetch, aws-core)\n2. **Role Layer**: Job-function specific configs (developer, SA, admin)\n3. **Personal Layer**: Individual customizations (preserved during updates)\n\n### **Smart Features:**\n\n- **Conflict Resolution**: Merge strategies for existing configs\n- **Selective Updates**: Update only specific components\n- **Profile Switching**: Easy switching between different work contexts\n- **Validation**: Pre-flight checks for dependencies and compatibility\n\n### **Questions for You:**\n\n1. **Target Audience**: Who will be using this? (Internal team, open source, enterprise?)\n2. **Update Strategy**: How often do you expect configurations to change?\n3. **Customization Level**: How much personalization should be preserved vs. standardized?\n4. **Dependencies**: Should the installer handle MCP server installations too?\n5. **Backup Strategy**: How aggressive should we be about preserving existing configs?\n\nWhat aspects of this approach resonate with your vision? Any specific requirements or constraints I should consider?"
        }
      }
    ],
    [
      {
        "additional_context": "",
        "env_context": {
          "env_state": {
            "operating_system": "macos",
            "current_working_directory": "/Users/janossch/dev/linux-configurations/.aws/amazonq",
            "environment_variables": []
          }
        },
        "content": {
          "Prompt": {
            "prompt": "the thing is, it should run on linux, windows, macos... would it be better to build an application that does this?"
          }
        },
        "images": null
      },
      {
        "Response": {
          "message_id": "0786ce31-711c-404f-bb32-78116eee5728",
          "content": "Great point! Cross-platform compatibility changes the game significantly. Let me think through the options:\n\n## Cross-Platform Approach Analysis\n\n### **Option 1: Shell Script + Platform Detection**\n```bash\n# Works but gets messy fast\nif [[ \"$OSTYPE\" == \"darwin\"* ]]; then\n    # macOS\nelif [[ \"$OSTYPE\" == \"linux-gnu\"* ]]; then\n    # Linux\nelif [[ \"$OSTYPE\" == \"msys\" ]] || [[ \"$OSTYPE\" == \"cygwin\" ]]; then\n    # Windows\nfi\n```\n**Pros**: Simple, no dependencies\n**Cons**: Windows compatibility nightmare, limited error handling\n\n### **Option 2: Python Application** ⭐ **RECOMMENDED**\n```python\n# Cross-platform by design\nimport platform\nimport shutil\nfrom pathlib import Path\n```\n**Pros**: \n- Native cross-platform support\n- Rich ecosystem (click, pydantic, rich for UI)\n- Easy JSON/YAML handling\n- Better error handling and validation\n- Can be packaged as standalone executable\n\n### **Option 3: Go Application**\n**Pros**: Single binary, fast, no runtime dependencies\n**Cons**: More complex for JSON manipulation, overkill for config management\n\n### **Option 4: Node.js Application**\n**Pros**: Great JSON handling, cross-platform\n**Cons**: Runtime dependency, larger footprint\n\n## **My Recommendation: Python CLI Application**\n\nHere's why Python makes the most sense:\n\n### **Architecture:**\n```\namazonq-config-manager/\n├── amazonq_config/\n│   ├── __init__.py\n│   ├── cli.py              # Click-based CLI\n│   ├── installer.py        # Core installation logic\n│   ├── config_manager.py   # Config file operations\n│   ├── platform_utils.py   # OS-specific paths/operations\n│   └── validators.py       # Configuration validation\n├── configs/                # Same as before\n├── contexts/              # Same as before\n├── hooks/                 # Same as before\n├── setup.py\n├── requirements.txt\n└── README.md\n```\n\n### **Installation Options:**\n```bash\n# Via pip (easiest)\npip install amazonq-config-manager\n\n# Via pipx (isolated)\npipx install amazonq-config-manager\n\n# Standalone executable (no Python needed)\n# Built with PyInstaller for each platform\n```\n\n### **Usage:**\n```bash\n# Install base configuration\namazonq-config install\n\n# Install with specific profile\namazonq-config install --profile solutions-architect\n\n# Update existing configuration\namazonq-config update --preserve-personal\n\n# Switch profiles\namazonq-config profile switch development\n\n# Validate current setup\namazonq-config validate\n\n# Backup current config\namazonq-config backup\n```\n\n### **Cross-Platform Benefits:**\n- **Path Handling**: `pathlib.Path` handles Windows/Unix paths automatically\n- **File Operations**: Python's `shutil` works everywhere\n- **JSON/YAML**: Native support with proper error handling\n- **User Input**: Rich prompts and confirmations\n- **Logging**: Proper logging with different levels\n- **Packaging**: Can create standalone executables for each platform\n\n### **Key Features:**\n1. **Smart Merging**: Intelligently merge existing configs\n2. **Rollback**: Easy rollback if something goes wrong\n3. **Validation**: Pre-flight checks for all dependencies\n4. **Interactive Mode**: Guided setup for new users\n5. **CI/CD Friendly**: Silent mode for automated deployments\n\nWould you like me to start with a basic Python CLI structure, or do you prefer a different approach? The Python route gives us the most flexibility and maintainability for cross-platform config management."
        }
      }
    ],
    [
      {
        "additional_context": "",
        "env_context": {
          "env_state": {
            "operating_system": "macos",
            "current_working_directory": "/Users/janossch/dev/linux-configurations/.aws/amazonq",
            "environment_variables": []
          }
        },
        "content": {
          "Prompt": {
            "prompt": "I think that's a good idea, let's do a python implementation. Let's move to a new folder and implement this freshly, let's use ~/dev/ai-configurator/ as folder... shall I `cd` into this for the remaining session? I think it would be good to create a task list there"
          }
        },
        "images": null
      },
      {
        "ToolUse": {
          "message_id": "dd926b4f-457b-4ba2-907a-dfc3ef65da37",
          "content": "Absolutely! Let's start fresh with a Python implementation. Yes, please `cd` into that directory - it'll make our work much cleaner.",
          "tool_uses": [
            {
              "id": "tooluse_u7--Ix6LQee9QICBZdbNtA",
              "name": "execute_bash",
              "orig_name": "execute_bash",
              "args": {
                "command": "mkdir -p ~/dev/ai-configurator && cd ~/dev/ai-configurator",
                "summary": "Create the ai-configurator directory"
              },
              "orig_args": {
                "command": "mkdir -p ~/dev/ai-configurator && cd ~/dev/ai-configurator",
                "summary": "Create the ai-configurator directory"
              }
            }
          ]
        }
      }
    ],
    [
      {
        "additional_context": "",
        "env_context": {
          "env_state": {
            "operating_system": "macos",
            "current_working_directory": "/Users/janossch/dev/linux-configurations/.aws/amazonq",
            "environment_variables": []
          }
        },
        "content": {
          "ToolUseResults": {
            "tool_use_results": [
              {
                "tool_use_id": "tooluse_u7--Ix6LQee9QICBZdbNtA",
                "content": [
                  {
                    "Json": {
                      "exit_status": "0",
                      "stdout": "",
                      "stderr": ""
                    }
                  }
                ],
                "status": "Success"
              }
            ]
          }
        },
        "images": null
      },
      {
        "ToolUse": {
          "message_id": "d2dbddab-52ac-4d97-bf05-d19fa8c8f879",
          "content": "Now let's create a comprehensive task list and project structure:",
          "tool_uses": [
            {
              "id": "tooluse_TZ7o9ErfR6WMCK3S_6RzFg",
              "name": "fs_write",
              "orig_name": "fs_write",
              "args": {
                "summary": "Create project task list and roadmap",
                "path": "~/dev/ai-configurator/TASKS.md",
                "file_text": "# AI Configurator - Task List\n\n## Project Overview\nCross-platform Python CLI tool for managing Amazon Q CLI configurations, contexts, profiles, and hooks.\n\n## Phase 1: Core Foundation ⏳\n- [ ] **Project Setup**\n  - [ ] Initialize Python project structure\n  - [ ] Setup pyproject.toml with dependencies\n  - [ ] Create virtual environment\n  - [ ] Setup basic CLI with Click\n  - [ ] Add logging configuration\n\n- [ ] **Platform Detection & Path Management**\n  - [ ] Implement cross-platform path detection for Amazon Q config\n  - [ ] Create platform-specific utilities (Windows/macOS/Linux)\n  - [ ] Handle different shell environments\n\n- [ ] **Configuration Management Core**\n  - [ ] JSON/YAML configuration parser\n  - [ ] Configuration validation system\n  - [ ] Backup and restore functionality\n  - [ ] Safe file operations with rollback\n\n## Phase 2: Installation System 🔄\n- [ ] **Base Installation**\n  - [ ] Detect existing Amazon Q CLI installation\n  - [ ] Backup existing configurations\n  - [ ] Install base configuration templates\n  - [ ] Validate installation success\n\n- [ ] **MCP Server Management**\n  - [ ] Modular MCP server configuration system\n  - [ ] Dependency checking for MCP servers\n  - [ ] Server installation and validation\n  - [ ] Server enable/disable functionality\n\n- [ ] **Profile System**\n  - [ ] Profile template system\n  - [ ] Profile switching mechanism\n  - [ ] Profile inheritance (base → role → personal)\n  - [ ] Profile validation\n\n## Phase 3: Advanced Features 🚀\n- [ ] **Context Management**\n  - [ ] Context file organization\n  - [ ] Dynamic context loading\n  - [ ] Context validation and testing\n  - [ ] Context sharing and templates\n\n- [ ] **Hook System**\n  - [ ] Hook installation and management\n  - [ ] Cross-platform hook execution\n  - [ ] Hook validation and testing\n  - [ ] Custom hook development support\n\n- [ ] **Update & Maintenance**\n  - [ ] Configuration update system\n  - [ ] Selective component updates\n  - [ ] Migration between versions\n  - [ ] Health check and diagnostics\n\n## Phase 4: Distribution & Polish ✨\n- [ ] **Packaging**\n  - [ ] PyPI package setup\n  - [ ] Standalone executable creation (PyInstaller)\n  - [ ] Platform-specific installers\n  - [ ] Docker container support\n\n- [ ] **Documentation**\n  - [ ] User guide and tutorials\n  - [ ] API documentation\n  - [ ] Configuration examples\n  - [ ] Troubleshooting guide\n\n- [ ] **Testing & Quality**\n  - [ ] Unit tests for all components\n  - [ ] Integration tests\n  - [ ] Cross-platform testing\n  - [ ] Performance optimization\n\n## Current Status: 🎯 Starting Phase 1\n\n## Next Immediate Tasks:\n1. Setup Python project structure\n2. Create basic CLI framework\n3. Implement platform detection\n4. Create configuration parser\n\n## Architecture Decisions Made:\n- **Language**: Python 3.8+ for cross-platform compatibility\n- **CLI Framework**: Click for robust command-line interface\n- **Config Format**: JSON for MCP configs, YAML for user configs\n- **Packaging**: PyPI + standalone executables\n- **Testing**: pytest with cross-platform CI\n\n## Dependencies Identified:\n- click (CLI framework)\n- pydantic (data validation)\n- rich (beautiful terminal output)\n- pathlib (cross-platform paths)\n- pyyaml (YAML support)\n- packaging (version management)\n\n---\n*Last Updated: $(date)*\n*Status: Planning → Implementation*",
                "command": "create"
              },
              "orig_args": {
                "summary": "Create project task list and roadmap",
                "path": "~/dev/ai-configurator/TASKS.md",
                "file_text": "# AI Configurator - Task List\n\n## Project Overview\nCross-platform Python CLI tool for managing Amazon Q CLI configurations, contexts, profiles, and hooks.\n\n## Phase 1: Core Foundation ⏳\n- [ ] **Project Setup**\n  - [ ] Initialize Python project structure\n  - [ ] Setup pyproject.toml with dependencies\n  - [ ] Create virtual environment\n  - [ ] Setup basic CLI with Click\n  - [ ] Add logging configuration\n\n- [ ] **Platform Detection & Path Management**\n  - [ ] Implement cross-platform path detection for Amazon Q config\n  - [ ] Create platform-specific utilities (Windows/macOS/Linux)\n  - [ ] Handle different shell environments\n\n- [ ] **Configuration Management Core**\n  - [ ] JSON/YAML configuration parser\n  - [ ] Configuration validation system\n  - [ ] Backup and restore functionality\n  - [ ] Safe file operations with rollback\n\n## Phase 2: Installation System 🔄\n- [ ] **Base Installation**\n  - [ ] Detect existing Amazon Q CLI installation\n  - [ ] Backup existing configurations\n  - [ ] Install base configuration templates\n  - [ ] Validate installation success\n\n- [ ] **MCP Server Management**\n  - [ ] Modular MCP server configuration system\n  - [ ] Dependency checking for MCP servers\n  - [ ] Server installation and validation\n  - [ ] Server enable/disable functionality\n\n- [ ] **Profile System**\n  - [ ] Profile template system\n  - [ ] Profile switching mechanism\n  - [ ] Profile inheritance (base → role → personal)\n  - [ ] Profile validation\n\n## Phase 3: Advanced Features 🚀\n- [ ] **Context Management**\n  - [ ] Context file organization\n  - [ ] Dynamic context loading\n  - [ ] Context validation and testing\n  - [ ] Context sharing and templates\n\n- [ ] **Hook System**\n  - [ ] Hook installation and management\n  - [ ] Cross-platform hook execution\n  - [ ] Hook validation and testing\n  - [ ] Custom hook development support\n\n- [ ] **Update & Maintenance**\n  - [ ] Configuration update system\n  - [ ] Selective component updates\n  - [ ] Migration between versions\n  - [ ] Health check and diagnostics\n\n## Phase 4: Distribution & Polish ✨\n- [ ] **Packaging**\n  - [ ] PyPI package setup\n  - [ ] Standalone executable creation (PyInstaller)\n  - [ ] Platform-specific installers\n  - [ ] Docker container support\n\n- [ ] **Documentation**\n  - [ ] User guide and tutorials\n  - [ ] API documentation\n  - [ ] Configuration examples\n  - [ ] Troubleshooting guide\n\n- [ ] **Testing & Quality**\n  - [ ] Unit tests for all components\n  - [ ] Integration tests\n  - [ ] Cross-platform testing\n  - [ ] Performance optimization\n\n## Current Status: 🎯 Starting Phase 1\n\n## Next Immediate Tasks:\n1. Setup Python project structure\n2. Create basic CLI framework\n3. Implement platform detection\n4. Create configuration parser\n\n## Architecture Decisions Made:\n- **Language**: Python 3.8+ for cross-platform compatibility\n- **CLI Framework**: Click for robust command-line interface\n- **Config Format**: JSON for MCP configs, YAML for user configs\n- **Packaging**: PyPI + standalone executables\n- **Testing**: pytest with cross-platform CI\n\n## Dependencies Identified:\n- click (CLI framework)\n- pydantic (data validation)\n- rich (beautiful terminal output)\n- pathlib (cross-platform paths)\n- pyyaml (YAML support)\n- packaging (version management)\n\n---\n*Last Updated: $(date)*\n*Status: Planning → Implementation*",
                "command": "create"
              }
            }
          ]
        }
      }
    ],
    [
      {
        "additional_context": "",
        "env_context": {
          "env_state": {
            "operating_system": "macos",
            "current_working_directory": "/Users/janossch/dev/linux-configurations/.aws/amazonq",
            "environment_variables": []
          }
        },
        "content": {
          "ToolUseResults": {
            "tool_use_results": [
              {
                "tool_use_id": "tooluse_TZ7o9ErfR6WMCK3S_6RzFg",
                "content": [
                  {
                    "Text": ""
                  }
                ],
                "status": "Success"
              }
            ]
          }
        },
        "images": null
      },
      {
        "ToolUse": {
          "message_id": "d47ba693-bdf3-42ab-b83d-cba8275ead8d",
          "content": "Now let's create the initial project structure:",
          "tool_uses": [
            {
              "id": "tooluse_olKRgFqCR7KDR197gFqm4w",
              "name": "fs_write",
              "orig_name": "fs_write",
              "args": {
                "summary": "Create project structure and pyproject.toml",
                "path": "~/dev/ai-configurator/pyproject.toml",
                "file_text": "[build-system]\nrequires = [\"hatchling\"]\nbuild-backend = \"hatchling.build\"\n\n[project]\nname = \"ai-configurator\"\nversion = \"0.1.0\"\ndescription = \"Cross-platform configuration manager for Amazon Q CLI\"\nreadme = \"README.md\"\nrequires-python = \">=3.8\"\nlicense = \"MIT\"\nauthors = [\n    { name = \"AI Configurator Team\" },\n]\nkeywords = [\"amazon-q\", \"cli\", \"configuration\", \"ai\", \"mcp\"]\nclassifiers = [\n    \"Development Status :: 3 - Alpha\",\n    \"Intended Audience :: Developers\",\n    \"License :: OSI Approved :: MIT License\",\n    \"Operating System :: OS Independent\",\n    \"Programming Language :: Python :: 3\",\n    \"Programming Language :: Python :: 3.8\",\n    \"Programming Language :: Python :: 3.9\",\n    \"Programming Language :: Python :: 3.10\",\n    \"Programming Language :: Python :: 3.11\",\n    \"Programming Language :: Python :: 3.12\",\n    \"Topic :: Software Development :: Tools\",\n    \"Topic :: System :: Installation/Setup\",\n]\n\ndependencies = [\n    \"click>=8.0.0\",\n    \"pydantic>=2.0.0\",\n    \"rich>=13.0.0\",\n    \"pyyaml>=6.0.0\",\n    \"packaging>=21.0.0\",\n    \"platformdirs>=3.0.0\",\n]\n\n[project.optional-dependencies]\ndev = [\n    \"pytest>=7.0.0\",\n    \"pytest-cov>=4.0.0\",\n    \"black>=23.0.0\",\n    \"isort>=5.0.0\",\n    \"flake8>=6.0.0\",\n    \"mypy>=1.0.0\",\n    \"pre-commit>=3.0.0\",\n]\n\n[project.urls]\nHomepage = \"https://github.com/your-org/ai-configurator\"\nDocumentation = \"https://ai-configurator.readthedocs.io\"\nRepository = \"https://github.com/your-org/ai-configurator.git\"\n\"Bug Tracker\" = \"https://github.com/your-org/ai-configurator/issues\"\n\n[project.scripts]\nai-config = \"ai_configurator.cli:main\"\n\n[tool.hatch.build.targets.wheel]\npackages = [\"src/ai_configurator\"]\n\n[tool.hatch.build.targets.sdist]\ninclude = [\n    \"/src\",\n    \"/configs\",\n    \"/contexts\",\n    \"/hooks\",\n    \"/templates\",\n]\n\n[tool.black]\nline-length = 88\ntarget-version = ['py38']\ninclude = '\\.pyi?$'\n\n[tool.isort]\nprofile = \"black\"\nmulti_line_output = 3\n\n[tool.mypy]\npython_version = \"3.8\"\nwarn_return_any = true\nwarn_unused_configs = true\ndisallow_untyped_defs = true\n\n[tool.pytest.ini_options]\ntestpaths = [\"tests\"]\npython_files = [\"test_*.py\"]\npython_classes = [\"Test*\"]\npython_functions = [\"test_*\"]\naddopts = \"--cov=ai_configurator --cov-report=term-missing\"",
                "command": "create"
              },
              "orig_args": {
                "summary": "Create project structure and pyproject.toml",
                "path": "~/dev/ai-configurator/pyproject.toml",
                "file_text": "[build-system]\nrequires = [\"hatchling\"]\nbuild-backend = \"hatchling.build\"\n\n[project]\nname = \"ai-configurator\"\nversion = \"0.1.0\"\ndescription = \"Cross-platform configuration manager for Amazon Q CLI\"\nreadme = \"README.md\"\nrequires-python = \">=3.8\"\nlicense = \"MIT\"\nauthors = [\n    { name = \"AI Configurator Team\" },\n]\nkeywords = [\"amazon-q\", \"cli\", \"configuration\", \"ai\", \"mcp\"]\nclassifiers = [\n    \"Development Status :: 3 - Alpha\",\n    \"Intended Audience :: Developers\",\n    \"License :: OSI Approved :: MIT License\",\n    \"Operating System :: OS Independent\",\n    \"Programming Language :: Python :: 3\",\n    \"Programming Language :: Python :: 3.8\",\n    \"Programming Language :: Python :: 3.9\",\n    \"Programming Language :: Python :: 3.10\",\n    \"Programming Language :: Python :: 3.11\",\n    \"Programming Language :: Python :: 3.12\",\n    \"Topic :: Software Development :: Tools\",\n    \"Topic :: System :: Installation/Setup\",\n]\n\ndependencies = [\n    \"click>=8.0.0\",\n    \"pydantic>=2.0.0\",\n    \"rich>=13.0.0\",\n    \"pyyaml>=6.0.0\",\n    \"packaging>=21.0.0\",\n    \"platformdirs>=3.0.0\",\n]\n\n[project.optional-dependencies]\ndev = [\n    \"pytest>=7.0.0\",\n    \"pytest-cov>=4.0.0\",\n    \"black>=23.0.0\",\n    \"isort>=5.0.0\",\n    \"flake8>=6.0.0\",\n    \"mypy>=1.0.0\",\n    \"pre-commit>=3.0.0\",\n]\n\n[project.urls]\nHomepage = \"https://github.com/your-org/ai-configurator\"\nDocumentation = \"https://ai-configurator.readthedocs.io\"\nRepository = \"https://github.com/your-org/ai-configurator.git\"\n\"Bug Tracker\" = \"https://github.com/your-org/ai-configurator/issues\"\n\n[project.scripts]\nai-config = \"ai_configurator.cli:main\"\n\n[tool.hatch.build.targets.wheel]\npackages = [\"src/ai_configurator\"]\n\n[tool.hatch.build.targets.sdist]\ninclude = [\n    \"/src\",\n    \"/configs\",\n    \"/contexts\",\n    \"/hooks\",\n    \"/templates\",\n]\n\n[tool.black]\nline-length = 88\ntarget-version = ['py38']\ninclude = '\\.pyi?$'\n\n[tool.isort]\nprofile = \"black\"\nmulti_line_output = 3\n\n[tool.mypy]\npython_version = \"3.8\"\nwarn_return_any = true\nwarn_unused_configs = true\ndisallow_untyped_defs = true\n\n[tool.pytest.ini_options]\ntestpaths = [\"tests\"]\npython_files = [\"test_*.py\"]\npython_classes = [\"Test*\"]\npython_functions = [\"test_*\"]\naddopts = \"--cov=ai_configurator --cov-report=term-missing\"",
                "command": "create"
              }
            }
          ]
        }
      }
    ],
    [
      {
        "additional_context": "",
        "env_context": {
          "env_state": {
            "operating_system": "macos",
            "current_working_directory": "/Users/janossch/dev/linux-configurations/.aws/amazonq",
            "environment_variables": []
          }
        },
        "content": {
          "ToolUseResults": {
            "tool_use_results": [
              {
                "tool_use_id": "tooluse_olKRgFqCR7KDR197gFqm4w",
                "content": [
                  {
                    "Text": ""
                  }
                ],
                "status": "Success"
              }
            ]
          }
        },
        "images": null
      },
      {
        "ToolUse": {
          "message_id": "0838b64b-2c82-4d0c-9b9b-76ad4850719c",
          "content": "",
          "tool_uses": [
            {
              "id": "tooluse_p-me3tZJRte_uWqilvR7Vg",
              "name": "execute_bash",
              "orig_name": "execute_bash",
              "args": {
                "summary": "Create the complete project directory structure",
                "command": "mkdir -p src/ai_configurator/{commands,core,utils} tests/{unit,integration} configs/{mcp-servers,profiles} contexts hooks templates docs"
              },
              "orig_args": {
                "summary": "Create the complete project directory structure",
                "command": "mkdir -p src/ai_configurator/{commands,core,utils} tests/{unit,integration} configs/{mcp-servers,profiles} contexts hooks templates docs"
              }
            }
          ]
        }
      }
    ],
    [
      {
        "additional_context": "",
        "env_context": {
          "env_state": {
            "operating_system": "macos",
            "current_working_directory": "/Users/janossch/dev/linux-configurations/.aws/amazonq",
            "environment_variables": []
          }
        },
        "content": {
          "ToolUseResults": {
            "tool_use_results": [
              {
                "tool_use_id": "tooluse_p-me3tZJRte_uWqilvR7Vg",
                "content": [
                  {
                    "Json": {
                      "exit_status": "0",
                      "stdout": "",
                      "stderr": ""
                    }
                  }
                ],
                "status": "Success"
              }
            ]
          }
        },
        "images": null
      },
      {
        "ToolUse": {
          "message_id": "70d4d60f-d9d6-483c-9288-44d6ca0d7528",
          "content": "",
          "tool_uses": [
            {
              "id": "tooluse_4wfaTJ3BTZO7fJ_DNb6ktA",
              "name": "fs_write",
              "orig_name": "fs_write",
              "args": {
                "summary": "Create README with project overview",
                "path": "~/dev/ai-configurator/README.md",
                "file_text": "# AI Configurator\n\nCross-platform configuration manager for Amazon Q CLI, contexts, profiles, and MCP servers.\n\n## 🎯 Purpose\n\nSimplify the setup and sharing of Amazon Q CLI configurations across teams and environments. Whether you're setting up a new machine, onboarding team members, or standardizing configurations across your organization, AI Configurator makes it seamless.\n\n## ✨ Features\n\n- **Cross-Platform**: Works on Windows, macOS, and Linux\n- **Modular Configuration**: Pick and choose components you need\n- **Profile Management**: Switch between different work contexts easily\n- **Safe Operations**: Automatic backups and rollback capabilities\n- **MCP Server Management**: Install and manage MCP servers effortlessly\n- **Context Sharing**: Share knowledge bases and contexts across teams\n- **Hook System**: Automate workflows with custom hooks\n\n## 🚀 Quick Start\n\n```bash\n# Install via pip\npip install ai-configurator\n\n# Install base configuration\nai-config install\n\n# Install with specific profile\nai-config install --profile solutions-architect\n\n# Switch between profiles\nai-config profile switch development\n```\n\n## 📋 Commands\n\n```bash\nai-config install [--profile PROFILE]     # Install configuration\nai-config update [--preserve-personal]    # Update existing config\nai-config profile list                    # List available profiles\nai-config profile switch PROFILE          # Switch to profile\nai-config backup                          # Backup current config\nai-config restore BACKUP_ID               # Restore from backup\nai-config validate                        # Validate current setup\nai-config status                          # Show configuration status\n```\n\n## 🏗️ Project Structure\n\n```\nai-configurator/\n├── src/ai_configurator/           # Main package\n│   ├── commands/                  # CLI command implementations\n│   ├── core/                      # Core functionality\n│   └── utils/                     # Utility functions\n├── configs/                       # Configuration templates\n│   ├── mcp-servers/              # MCP server definitions\n│   └── profiles/                 # Profile templates\n├── contexts/                      # Shared context files\n├── hooks/                        # Hook scripts\n└── templates/                    # Configuration templates\n```\n\n## 🛠️ Development\n\n```bash\n# Clone and setup\ngit clone https://github.com/your-org/ai-configurator.git\ncd ai-configurator\n\n# Create virtual environment\npython -m venv venv\nsource venv/bin/activate  # On Windows: venv\\Scripts\\activate\n\n# Install in development mode\npip install -e \".[dev]\"\n\n# Run tests\npytest\n\n# Format code\nblack src/ tests/\nisort src/ tests/\n```\n\n## 📖 Documentation\n\n- [Installation Guide](docs/installation.md)\n- [Configuration Guide](docs/configuration.md)\n- [Profile Management](docs/profiles.md)\n- [MCP Server Setup](docs/mcp-servers.md)\n- [Custom Hooks](docs/hooks.md)\n- [Troubleshooting](docs/troubleshooting.md)\n\n## 🤝 Contributing\n\nWe welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.\n\n## 📄 License\n\nMIT License - see [LICENSE](LICENSE) for details.\n\n## 🆘 Support\n\n- [GitHub Issues](https://github.com/your-org/ai-configurator/issues)\n- [Documentation](https://ai-configurator.readthedocs.io)\n- [Discussions](https://github.com/your-org/ai-configurator/discussions)\n\n---\n\n**Status**: 🚧 Under Development - Alpha Release",
                "command": "create"
              },
              "orig_args": {
                "summary": "Create README with project overview",
                "path": "~/dev/ai-configurator/README.md",
                "file_text": "# AI Configurator\n\nCross-platform configuration manager for Amazon Q CLI, contexts, profiles, and MCP servers.\n\n## 🎯 Purpose\n\nSimplify the setup and sharing of Amazon Q CLI configurations across teams and environments. Whether you're setting up a new machine, onboarding team members, or standardizing configurations across your organization, AI Configurator makes it seamless.\n\n## ✨ Features\n\n- **Cross-Platform**: Works on Windows, macOS, and Linux\n- **Modular Configuration**: Pick and choose components you need\n- **Profile Management**: Switch between different work contexts easily\n- **Safe Operations**: Automatic backups and rollback capabilities\n- **MCP Server Management**: Install and manage MCP servers effortlessly\n- **Context Sharing**: Share knowledge bases and contexts across teams\n- **Hook System**: Automate workflows with custom hooks\n\n## 🚀 Quick Start\n\n```bash\n# Install via pip\npip install ai-configurator\n\n# Install base configuration\nai-config install\n\n# Install with specific profile\nai-config install --profile solutions-architect\n\n# Switch between profiles\nai-config profile switch development\n```\n\n## 📋 Commands\n\n```bash\nai-config install [--profile PROFILE]     # Install configuration\nai-config update [--preserve-personal]    # Update existing config\nai-config profile list                    # List available profiles\nai-config profile switch PROFILE          # Switch to profile\nai-config backup                          # Backup current config\nai-config restore BACKUP_ID               # Restore from backup\nai-config validate                        # Validate current setup\nai-config status                          # Show configuration status\n```\n\n## 🏗️ Project Structure\n\n```\nai-configurator/\n├── src/ai_configurator/           # Main package\n│   ├── commands/                  # CLI command implementations\n│   ├── core/                      # Core functionality\n│   └── utils/                     # Utility functions\n├── configs/                       # Configuration templates\n│   ├── mcp-servers/              # MCP server definitions\n│   └── profiles/                 # Profile templates\n├── contexts/                      # Shared context files\n├── hooks/                        # Hook scripts\n└── templates/                    # Configuration templates\n```\n\n## 🛠️ Development\n\n```bash\n# Clone and setup\ngit clone https://github.com/your-org/ai-configurator.git\ncd ai-configurator\n\n# Create virtual environment\npython -m venv venv\nsource venv/bin/activate  # On Windows: venv\\Scripts\\activate\n\n# Install in development mode\npip install -e \".[dev]\"\n\n# Run tests\npytest\n\n# Format code\nblack src/ tests/\nisort src/ tests/\n```\n\n## 📖 Documentation\n\n- [Installation Guide](docs/installation.md)\n- [Configuration Guide](docs/configuration.md)\n- [Profile Management](docs/profiles.md)\n- [MCP Server Setup](docs/mcp-servers.md)\n- [Custom Hooks](docs/hooks.md)\n- [Troubleshooting](docs/troubleshooting.md)\n\n## 🤝 Contributing\n\nWe welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.\n\n## 📄 License\n\nMIT License - see [LICENSE](LICENSE) for details.\n\n## 🆘 Support\n\n- [GitHub Issues](https://github.com/your-org/ai-configurator/issues)\n- [Documentation](https://ai-configurator.readthedocs.io)\n- [Discussions](https://github.com/your-org/ai-configurator/discussions)\n\n---\n\n**Status**: 🚧 Under Development - Alpha Release",
                "command": "create"
              }
            }
          ]
        }
      }
    ],
    [
      {
        "additional_context": "",
        "env_context": {
          "env_state": {
            "operating_system": "macos",
            "current_working_directory": "/Users/janossch/dev/linux-configurations/.aws/amazonq",
            "environment_variables": []
          }
        },
        "content": {
          "ToolUseResults": {
            "tool_use_results": [
              {
                "tool_use_id": "tooluse_4wfaTJ3BTZO7fJ_DNb6ktA",
                "content": [
                  {
                    "Text": ""
                  }
                ],
                "status": "Success"
              }
            ]
          }
        },
        "images": null
      },
      {
        "ToolUse": {
          "message_id": "c70b7c7e-e695-4b94-8ce3-43cc4c23f3c3",
          "content": "Now let's create the basic CLI structure:",
          "tool_uses": [
            {
              "id": "tooluse_OQ0PZ0xsRzebmqW-TsXgsA",
              "name": "fs_write",
              "orig_name": "fs_write",
              "args": {
                "summary": "Create main CLI entry point",
                "path": "~/dev/ai-configurator/src/ai_configurator/__init__.py",
                "file_text": "\"\"\"AI Configurator - Cross-platform configuration manager for Amazon Q CLI.\"\"\"\n\n__version__ = \"0.1.0\"\n__author__ = \"AI Configurator Team\"\n__description__ = \"Cross-platform configuration manager for Amazon Q CLI\"",
                "command": "create"
              },
              "orig_args": {
                "summary": "Create main CLI entry point",
                "path": "~/dev/ai-configurator/src/ai_configurator/__init__.py",
                "file_text": "\"\"\"AI Configurator - Cross-platform configuration manager for Amazon Q CLI.\"\"\"\n\n__version__ = \"0.1.0\"\n__author__ = \"AI Configurator Team\"\n__description__ = \"Cross-platform configuration manager for Amazon Q CLI\"",
                "command": "create"
              }
            }
          ]
        }
      }
    ],
    [
      {
        "additional_context": "",
        "env_context": {
          "env_state": {
            "operating_system": "macos",
            "current_working_directory": "/Users/janossch/dev/linux-configurations/.aws/amazonq",
            "environment_variables": []
          }
        },
        "content": {
          "ToolUseResults": {
            "tool_use_results": [
              {
                "tool_use_id": "tooluse_OQ0PZ0xsRzebmqW-TsXgsA",
                "content": [
                  {
                    "Text": ""
                  }
                ],
                "status": "Success"
              }
            ]
          }
        },
        "images": null
      },
      {
        "ToolUse": {
          "message_id": "08818367-f756-4700-8cac-ad0726e4e030",
          "content": "",
          "tool_uses": [
            {
              "id": "tooluse_uCU81-x-Tw6paJbqRbWesA",
              "name": "fs_write",
              "orig_name": "fs_write",
              "args": {
                "summary": "Create main CLI module with Click framework",
                "path": "~/dev/ai-configurator/src/ai_configurator/cli.py",
                "file_text": "\"\"\"Main CLI interface for AI Configurator.\"\"\"\n\nimport sys\nfrom typing import Optional\n\nimport click\nfrom rich.console import Console\nfrom rich.panel import Panel\n\nfrom . import __version__\nfrom .core.platform import PlatformManager\nfrom .utils.logging import setup_logging\n\nconsole = Console()\n\n\n@click.group()\n@click.version_option(version=__version__)\n@click.option(\n    \"--verbose\", \"-v\", \n    is_flag=True, \n    help=\"Enable verbose output\"\n)\n@click.option(\n    \"--quiet\", \"-q\", \n    is_flag=True, \n    help=\"Suppress non-error output\"\n)\n@click.pass_context\ndef cli(ctx: click.Context, verbose: bool, quiet: bool) -> None:\n    \"\"\"AI Configurator - Cross-platform configuration manager for Amazon Q CLI.\"\"\"\n    ctx.ensure_object(dict)\n    ctx.obj[\"verbose\"] = verbose\n    ctx.obj[\"quiet\"] = quiet\n    \n    # Setup logging\n    log_level = \"DEBUG\" if verbose else \"WARNING\" if quiet else \"INFO\"\n    setup_logging(log_level)\n    \n    # Initialize platform manager\n    ctx.obj[\"platform\"] = PlatformManager()\n\n\n@cli.command()\n@click.option(\n    \"--profile\", \"-p\",\n    help=\"Install with specific profile (e.g., developer, solutions-architect)\"\n)\n@click.option(\n    \"--mcp-servers\",\n    help=\"Comma-separated list of MCP server groups to install\"\n)\n@click.option(\n    \"--force\", \"-f\",\n    is_flag=True,\n    help=\"Force installation even if configuration exists\"\n)\n@click.pass_context\ndef install(ctx: click.Context, profile: Optional[str], mcp_servers: Optional[str], force: bool) -> None:\n    \"\"\"Install Amazon Q CLI configuration.\"\"\"\n    if not ctx.obj[\"quiet\"]:\n        console.print(Panel.fit(\n            \"[bold blue]AI Configurator Installation[/bold blue]\\n\"\n            \"Setting up your Amazon Q CLI configuration...\",\n            border_style=\"blue\"\n        ))\n    \n    platform = ctx.obj[\"platform\"]\n    \n    # Check if Amazon Q CLI is installed\n    if not platform.is_amazonq_installed():\n        console.print(\"[red]Error: Amazon Q CLI not found. Please install it first.[/red]\")\n        sys.exit(1)\n    \n    # TODO: Implement installation logic\n    console.print(\"[yellow]Installation functionality coming soon![/yellow]\")\n\n\n@cli.command()\n@click.option(\n    \"--preserve-personal\",\n    is_flag=True,\n    help=\"Preserve personal customizations during update\"\n)\n@click.pass_context\ndef update(ctx: click.Context, preserve_personal: bool) -> None:\n    \"\"\"Update existing Amazon Q CLI configuration.\"\"\"\n    console.print(\"[yellow]Update functionality coming soon![/yellow]\")\n\n\n@cli.group()\ndef profile() -> None:\n    \"\"\"Manage configuration profiles.\"\"\"\n    pass\n\n\n@profile.command(\"list\")\n@click.pass_context\ndef profile_list(ctx: click.Context) -> None:\n    \"\"\"List available profiles.\"\"\"\n    console.print(\"[yellow]Profile listing functionality coming soon![/yellow]\")\n\n\n@profile.command(\"switch\")\n@click.argument(\"profile_name\")\n@click.pass_context\ndef profile_switch(ctx: click.Context, profile_name: str) -> None:\n    \"\"\"Switch to a different profile.\"\"\"\n    console.print(f\"[yellow]Switching to profile '{profile_name}' - functionality coming soon![/yellow]\")\n\n\n@cli.command()\n@click.pass_context\ndef backup(ctx: click.Context) -> None:\n    \"\"\"Backup current configuration.\"\"\"\n    console.print(\"[yellow]Backup functionality coming soon![/yellow]\")\n\n\n@cli.command()\n@click.argument(\"backup_id\")\n@click.pass_context\ndef restore(ctx: click.Context, backup_id: str) -> None:\n    \"\"\"Restore configuration from backup.\"\"\"\n    console.print(f\"[yellow]Restoring backup '{backup_id}' - functionality coming soon![/yellow]\")\n\n\n@cli.command()\n@click.pass_context\ndef validate(ctx: click.Context) -> None:\n    \"\"\"Validate current configuration.\"\"\"\n    platform = ctx.obj[\"platform\"]\n    \n    console.print(\"[bold blue]Validating Amazon Q CLI Configuration[/bold blue]\\n\")\n    \n    # Check Amazon Q CLI installation\n    if platform.is_amazonq_installed():\n        console.print(\"✅ Amazon Q CLI: [green]Found[/green]\")\n    else:\n        console.print(\"❌ Amazon Q CLI: [red]Not found[/red]\")\n    \n    # Check configuration directory\n    config_dir = platform.get_amazonq_config_dir()\n    if config_dir.exists():\n        console.print(f\"✅ Config Directory: [green]{config_dir}[/green]\")\n    else:\n        console.print(f\"❌ Config Directory: [red]{config_dir} (not found)[/red]\")\n    \n    console.print(\"[yellow]Full validation functionality coming soon![/yellow]\")\n\n\n@cli.command()\n@click.pass_context\ndef status(ctx: click.Context) -> None:\n    \"\"\"Show current configuration status.\"\"\"\n    platform = ctx.obj[\"platform\"]\n    \n    console.print(Panel.fit(\n        f\"[bold]Platform:[/bold] {platform.get_platform_name()}\\n\"\n        f\"[bold]Amazon Q Config:[/bold] {platform.get_amazonq_config_dir()}\\n\"\n        f\"[bold]Version:[/bold] {__version__}\",\n        title=\"AI Configurator Status\",\n        border_style=\"green\"\n    ))\n\n\ndef main() -> None:\n    \"\"\"Main entry point for the CLI.\"\"\"\n    try:\n        cli()\n    except KeyboardInterrupt:\n        console.print(\"\\n[yellow]Operation cancelled by user.[/yellow]\")\n        sys.exit(1)\n    except Exception as e:\n        console.print(f\"[red]Error: {e}[/red]\")\n        sys.exit(1)\n\n\nif __name__ == \"__main__\":\n    main()",
                "command": "create"
              },
              "orig_args": {
                "summary": "Create main CLI module with Click framework",
                "path": "~/dev/ai-configurator/src/ai_configurator/cli.py",
                "file_text": "\"\"\"Main CLI interface for AI Configurator.\"\"\"\n\nimport sys\nfrom typing import Optional\n\nimport click\nfrom rich.console import Console\nfrom rich.panel import Panel\n\nfrom . import __version__\nfrom .core.platform import PlatformManager\nfrom .utils.logging import setup_logging\n\nconsole = Console()\n\n\n@click.group()\n@click.version_option(version=__version__)\n@click.option(\n    \"--verbose\", \"-v\", \n    is_flag=True, \n    help=\"Enable verbose output\"\n)\n@click.option(\n    \"--quiet\", \"-q\", \n    is_flag=True, \n    help=\"Suppress non-error output\"\n)\n@click.pass_context\ndef cli(ctx: click.Context, verbose: bool, quiet: bool) -> None:\n    \"\"\"AI Configurator - Cross-platform configuration manager for Amazon Q CLI.\"\"\"\n    ctx.ensure_object(dict)\n    ctx.obj[\"verbose\"] = verbose\n    ctx.obj[\"quiet\"] = quiet\n    \n    # Setup logging\n    log_level = \"DEBUG\" if verbose else \"WARNING\" if quiet else \"INFO\"\n    setup_logging(log_level)\n    \n    # Initialize platform manager\n    ctx.obj[\"platform\"] = PlatformManager()\n\n\n@cli.command()\n@click.option(\n    \"--profile\", \"-p\",\n    help=\"Install with specific profile (e.g., developer, solutions-architect)\"\n)\n@click.option(\n    \"--mcp-servers\",\n    help=\"Comma-separated list of MCP server groups to install\"\n)\n@click.option(\n    \"--force\", \"-f\",\n    is_flag=True,\n    help=\"Force installation even if configuration exists\"\n)\n@click.pass_context\ndef install(ctx: click.Context, profile: Optional[str], mcp_servers: Optional[str], force: bool) -> None:\n    \"\"\"Install Amazon Q CLI configuration.\"\"\"\n    if not ctx.obj[\"quiet\"]:\n        console.print(Panel.fit(\n            \"[bold blue]AI Configurator Installation[/bold blue]\\n\"\n            \"Setting up your Amazon Q CLI configuration...\",\n            border_style=\"blue\"\n        ))\n    \n    platform = ctx.obj[\"platform\"]\n    \n    # Check if Amazon Q CLI is installed\n    if not platform.is_amazonq_installed():\n        console.print(\"[red]Error: Amazon Q CLI not found. Please install it first.[/red]\")\n        sys.exit(1)\n    \n    # TODO: Implement installation logic\n    console.print(\"[yellow]Installation functionality coming soon![/yellow]\")\n\n\n@cli.command()\n@click.option(\n    \"--preserve-personal\",\n    is_flag=True,\n    help=\"Preserve personal customizations during update\"\n)\n@click.pass_context\ndef update(ctx: click.Context, preserve_personal: bool) -> None:\n    \"\"\"Update existing Amazon Q CLI configuration.\"\"\"\n    console.print(\"[yellow]Update functionality coming soon![/yellow]\")\n\n\n@cli.group()\ndef profile() -> None:\n    \"\"\"Manage configuration profiles.\"\"\"\n    pass\n\n\n@profile.command(\"list\")\n@click.pass_context\ndef profile_list(ctx: click.Context) -> None:\n    \"\"\"List available profiles.\"\"\"\n    console.print(\"[yellow]Profile listing functionality coming soon![/yellow]\")\n\n\n@profile.command(\"switch\")\n@click.argument(\"profile_name\")\n@click.pass_context\ndef profile_switch(ctx: click.Context, profile_name: str) -> None:\n    \"\"\"Switch to a different profile.\"\"\"\n    console.print(f\"[yellow]Switching to profile '{profile_name}' - functionality coming soon![/yellow]\")\n\n\n@cli.command()\n@click.pass_context\ndef backup(ctx: click.Context) -> None:\n    \"\"\"Backup current configuration.\"\"\"\n    console.print(\"[yellow]Backup functionality coming soon![/yellow]\")\n\n\n@cli.command()\n@click.argument(\"backup_id\")\n@click.pass_context\ndef restore(ctx: click.Context, backup_id: str) -> None:\n    \"\"\"Restore configuration from backup.\"\"\"\n    console.print(f\"[yellow]Restoring backup '{backup_id}' - functionality coming soon![/yellow]\")\n\n\n@cli.command()\n@click.pass_context\ndef validate(ctx: click.Context) -> None:\n    \"\"\"Validate current configuration.\"\"\"\n    platform = ctx.obj[\"platform\"]\n    \n    console.print(\"[bold blue]Validating Amazon Q CLI Configuration[/bold blue]\\n\")\n    \n    # Check Amazon Q CLI installation\n    if platform.is_amazonq_installed():\n        console.print(\"✅ Amazon Q CLI: [green]Found[/green]\")\n    else:\n        console.print(\"❌ Amazon Q CLI: [red]Not found[/red]\")\n    \n    # Check configuration directory\n    config_dir = platform.get_amazonq_config_dir()\n    if config_dir.exists():\n        console.print(f\"✅ Config Directory: [green]{config_dir}[/green]\")\n    else:\n        console.print(f\"❌ Config Directory: [red]{config_dir} (not found)[/red]\")\n    \n    console.print(\"[yellow]Full validation functionality coming soon![/yellow]\")\n\n\n@cli.command()\n@click.pass_context\ndef status(ctx: click.Context) -> None:\n    \"\"\"Show current configuration status.\"\"\"\n    platform = ctx.obj[\"platform\"]\n    \n    console.print(Panel.fit(\n        f\"[bold]Platform:[/bold] {platform.get_platform_name()}\\n\"\n        f\"[bold]Amazon Q Config:[/bold] {platform.get_amazonq_config_dir()}\\n\"\n        f\"[bold]Version:[/bold] {__version__}\",\n        title=\"AI Configurator Status\",\n        border_style=\"green\"\n    ))\n\n\ndef main() -> None:\n    \"\"\"Main entry point for the CLI.\"\"\"\n    try:\n        cli()\n    except KeyboardInterrupt:\n        console.print(\"\\n[yellow]Operation cancelled by user.[/yellow]\")\n        sys.exit(1)\n    except Exception as e:\n        console.print(f\"[red]Error: {e}[/red]\")\n        sys.exit(1)\n\n\nif __name__ == \"__main__\":\n    main()",
                "command": "create"
              }
            }
          ]
        }
      }
    ],
    [
      {
        "additional_context": "",
        "env_context": {
          "env_state": {
            "operating_system": "macos",
            "current_working_directory": "/Users/janossch/dev/linux-configurations/.aws/amazonq",
            "environment_variables": []
          }
        },
        "content": {
          "ToolUseResults": {
            "tool_use_results": [
              {
                "tool_use_id": "tooluse_uCU81-x-Tw6paJbqRbWesA",
                "content": [
                  {
                    "Text": ""
                  }
                ],
                "status": "Success"
              }
            ]
          }
        },
        "images": null
      },
      {
        "ToolUse": {
          "message_id": "419b5f64-a0cc-4df6-8f5a-4f378b019155",
          "content": "Now let's create the core platform management module:",
          "tool_uses": [
            {
              "id": "tooluse_AYHIab3IRiypwcVU3d3ckQ",
              "name": "fs_write",
              "orig_name": "fs_write",
              "args": {
                "summary": "Create platform detection and management module",
                "path": "~/dev/ai-configurator/src/ai_configurator/core/platform.py",
                "file_text": "\"\"\"Platform-specific utilities and path management.\"\"\"\n\nimport platform\nimport shutil\nfrom pathlib import Path\nfrom typing import Optional\n\nimport platformdirs\n\n\nclass PlatformManager:\n    \"\"\"Manages platform-specific operations and paths.\"\"\"\n    \n    def __init__(self) -> None:\n        self._platform = platform.system().lower()\n        self._home = Path.home()\n    \n    def get_platform_name(self) -> str:\n        \"\"\"Get the current platform name.\"\"\"\n        return self._platform.title()\n    \n    def is_windows(self) -> bool:\n        \"\"\"Check if running on Windows.\"\"\"\n        return self._platform == \"windows\"\n    \n    def is_macos(self) -> bool:\n        \"\"\"Check if running on macOS.\"\"\"\n        return self._platform == \"darwin\"\n    \n    def is_linux(self) -> bool:\n        \"\"\"Check if running on Linux.\"\"\"\n        return self._platform == \"linux\"\n    \n    def get_amazonq_config_dir(self) -> Path:\n        \"\"\"Get the Amazon Q CLI configuration directory.\"\"\"\n        if self.is_windows():\n            # Windows: %USERPROFILE%\\.aws\\amazonq\n            return self._home / \".aws\" / \"amazonq\"\n        else:\n            # macOS/Linux: ~/.aws/amazonq\n            return self._home / \".aws\" / \"amazonq\"\n    \n    def get_app_data_dir(self) -> Path:\n        \"\"\"Get the application data directory for AI Configurator.\"\"\"\n        return Path(platformdirs.user_data_dir(\"ai-configurator\", \"ai-configurator\"))\n    \n    def get_app_config_dir(self) -> Path:\n        \"\"\"Get the application configuration directory for AI Configurator.\"\"\"\n        return Path(platformdirs.user_config_dir(\"ai-configurator\", \"ai-configurator\"))\n    \n    def get_app_cache_dir(self) -> Path:\n        \"\"\"Get the application cache directory for AI Configurator.\"\"\"\n        return Path(platformdirs.user_cache_dir(\"ai-configurator\", \"ai-configurator\"))\n    \n    def is_amazonq_installed(self) -> bool:\n        \"\"\"Check if Amazon Q CLI is installed and accessible.\"\"\"\n        return shutil.which(\"q\") is not None\n    \n    def get_amazonq_version(self) -> Optional[str]:\n        \"\"\"Get the installed Amazon Q CLI version.\"\"\"\n        import subprocess\n        \n        try:\n            result = subprocess.run(\n                [\"q\", \"--version\"],\n                capture_output=True,\n                text=True,\n                timeout=10\n            )\n            if result.returncode == 0:\n                # Extract version from output (format may vary)\n                return result.stdout.strip()\n            return None\n        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):\n            return None\n    \n    def ensure_directories(self) -> None:\n        \"\"\"Ensure all necessary directories exist.\"\"\"\n        directories = [\n            self.get_app_data_dir(),\n            self.get_app_config_dir(),\n            self.get_app_cache_dir(),\n        ]\n        \n        for directory in directories:\n            directory.mkdir(parents=True, exist_ok=True)\n    \n    def get_shell_type(self) -> str:\n        \"\"\"Detect the current shell type.\"\"\"\n        import os\n        \n        shell = os.environ.get(\"SHELL\", \"\")\n        if \"bash\" in shell:\n            return \"bash\"\n        elif \"zsh\" in shell:\n            return \"zsh\"\n        elif \"fish\" in shell:\n            return \"fish\"\n        elif self.is_windows():\n            # Check for PowerShell vs Command Prompt\n            if os.environ.get(\"PSModulePath\"):\n                return \"powershell\"\n            else:\n                return \"cmd\"\n        else:\n            return \"unknown\"\n    \n    def get_executable_extension(self) -> str:\n        \"\"\"Get the executable file extension for the current platform.\"\"\"\n        return \".exe\" if self.is_windows() else \"\"\n    \n    def get_script_extension(self) -> str:\n        \"\"\"Get the script file extension for the current platform.\"\"\"\n        if self.is_windows():\n            shell = self.get_shell_type()\n            if shell == \"powershell\":\n                return \".ps1\"\n            else:\n                return \".bat\"\n        else:\n            return \".sh\"",
                "command": "create"
              },
              "orig_args": {
                "summary": "Create platform detection and management module",
                "path": "~/dev/ai-configurator/src/ai_configurator/core/platform.py",
                "file_text": "\"\"\"Platform-specific utilities and path management.\"\"\"\n\nimport platform\nimport shutil\nfrom pathlib import Path\nfrom typing import Optional\n\nimport platformdirs\n\n\nclass PlatformManager:\n    \"\"\"Manages platform-specific operations and paths.\"\"\"\n    \n    def __init__(self) -> None:\n        self._platform = platform.system().lower()\n        self._home = Path.home()\n    \n    def get_platform_name(self) -> str:\n        \"\"\"Get the current platform name.\"\"\"\n        return self._platform.title()\n    \n    def is_windows(self) -> bool:\n        \"\"\"Check if running on Windows.\"\"\"\n        return self._platform == \"windows\"\n    \n    def is_macos(self) -> bool:\n        \"\"\"Check if running on macOS.\"\"\"\n        return self._platform == \"darwin\"\n    \n    def is_linux(self) -> bool:\n        \"\"\"Check if running on Linux.\"\"\"\n        return self._platform == \"linux\"\n    \n    def get_amazonq_config_dir(self) -> Path:\n        \"\"\"Get the Amazon Q CLI configuration directory.\"\"\"\n        if self.is_windows():\n            # Windows: %USERPROFILE%\\.aws\\amazonq\n            return self._home / \".aws\" / \"amazonq\"\n        else:\n            # macOS/Linux: ~/.aws/amazonq\n            return self._home / \".aws\" / \"amazonq\"\n    \n    def get_app_data_dir(self) -> Path:\n        \"\"\"Get the application data directory for AI Configurator.\"\"\"\n        return Path(platformdirs.user_data_dir(\"ai-configurator\", \"ai-configurator\"))\n    \n    def get_app_config_dir(self) -> Path:\n        \"\"\"Get the application configuration directory for AI Configurator.\"\"\"\n        return Path(platformdirs.user_config_dir(\"ai-configurator\", \"ai-configurator\"))\n    \n    def get_app_cache_dir(self) -> Path:\n        \"\"\"Get the application cache directory for AI Configurator.\"\"\"\n        return Path(platformdirs.user_cache_dir(\"ai-configurator\", \"ai-configurator\"))\n    \n    def is_amazonq_installed(self) -> bool:\n        \"\"\"Check if Amazon Q CLI is installed and accessible.\"\"\"\n        return shutil.which(\"q\") is not None\n    \n    def get_amazonq_version(self) -> Optional[str]:\n        \"\"\"Get the installed Amazon Q CLI version.\"\"\"\n        import subprocess\n        \n        try:\n            result = subprocess.run(\n                [\"q\", \"--version\"],\n                capture_output=True,\n                text=True,\n                timeout=10\n            )\n            if result.returncode == 0:\n                # Extract version from output (format may vary)\n                return result.stdout.strip()\n            return None\n        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):\n            return None\n    \n    def ensure_directories(self) -> None:\n        \"\"\"Ensure all necessary directories exist.\"\"\"\n        directories = [\n            self.get_app_data_dir(),\n            self.get_app_config_dir(),\n            self.get_app_cache_dir(),\n        ]\n        \n        for directory in directories:\n            directory.mkdir(parents=True, exist_ok=True)\n    \n    def get_shell_type(self) -> str:\n        \"\"\"Detect the current shell type.\"\"\"\n        import os\n        \n        shell = os.environ.get(\"SHELL\", \"\")\n        if \"bash\" in shell:\n            return \"bash\"\n        elif \"zsh\" in shell:\n            return \"zsh\"\n        elif \"fish\" in shell:\n            return \"fish\"\n        elif self.is_windows():\n            # Check for PowerShell vs Command Prompt\n            if os.environ.get(\"PSModulePath\"):\n                return \"powershell\"\n            else:\n                return \"cmd\"\n        else:\n            return \"unknown\"\n    \n    def get_executable_extension(self) -> str:\n        \"\"\"Get the executable file extension for the current platform.\"\"\"\n        return \".exe\" if self.is_windows() else \"\"\n    \n    def get_script_extension(self) -> str:\n        \"\"\"Get the script file extension for the current platform.\"\"\"\n        if self.is_windows():\n            shell = self.get_shell_type()\n            if shell == \"powershell\":\n                return \".ps1\"\n            else:\n                return \".bat\"\n        else:\n            return \".sh\"",
                "command": "create"
              }
            }
          ]
        }
      }
    ],
    [
      {
        "additional_context": "",
        "env_context": {
          "env_state": {
            "operating_system": "macos",
            "current_working_directory": "/Users/janossch/dev/linux-configurations/.aws/amazonq",
            "environment_variables": []
          }
        },
        "content": {
          "ToolUseResults": {
            "tool_use_results": [
              {
                "tool_use_id": "tooluse_AYHIab3IRiypwcVU3d3ckQ",
                "content": [
                  {
                    "Text": ""
                  }
                ],
                "status": "Success"
              }
            ]
          }
        },
        "images": null
      },
      {
        "ToolUse": {
          "message_id": "c73df9e4-48ac-4401-8fa7-d1e2138baf4c",
          "content": "",
          "tool_uses": [
            {
              "id": "tooluse_ar81lK7FS9-DJJWG7pITlw",
              "name": "fs_write",
              "orig_name": "fs_write",
              "args": {
                "summary": "Create logging utility module",
                "path": "~/dev/ai-configurator/src/ai_configurator/utils/logging.py",
                "file_text": "\"\"\"Logging configuration and utilities.\"\"\"\n\nimport logging\nimport sys\nfrom pathlib import Path\nfrom typing import Optional\n\nfrom rich.console import Console\nfrom rich.logging import RichHandler\n\nconsole = Console()\n\n\ndef setup_logging(level: str = \"INFO\", log_file: Optional[Path] = None) -> None:\n    \"\"\"Setup logging configuration with Rich handler.\"\"\"\n    \n    # Convert string level to logging constant\n    numeric_level = getattr(logging, level.upper(), logging.INFO)\n    \n    # Create logger\n    logger = logging.getLogger(\"ai_configurator\")\n    logger.setLevel(numeric_level)\n    \n    # Clear any existing handlers\n    logger.handlers.clear()\n    \n    # Create Rich handler for console output\n    rich_handler = RichHandler(\n        console=console,\n        show_time=False,\n        show_path=False,\n        markup=True,\n        rich_tracebacks=True\n    )\n    rich_handler.setLevel(numeric_level)\n    \n    # Create formatter\n    formatter = logging.Formatter(\n        fmt=\"%(message)s\",\n        datefmt=\"[%X]\"\n    )\n    rich_handler.setFormatter(formatter)\n    \n    # Add handler to logger\n    logger.addHandler(rich_handler)\n    \n    # Add file handler if log_file is specified\n    if log_file:\n        log_file.parent.mkdir(parents=True, exist_ok=True)\n        file_handler = logging.FileHandler(log_file)\n        file_handler.setLevel(logging.DEBUG)  # Always log everything to file\n        \n        file_formatter = logging.Formatter(\n            fmt=\"%(asctime)s - %(name)s - %(levelname)s - %(message)s\",\n            datefmt=\"%Y-%m-%d %H:%M:%S\"\n        )\n        file_handler.setFormatter(file_formatter)\n        logger.addHandler(file_handler)\n    \n    # Set root logger level to prevent other libraries from being too verbose\n    logging.getLogger().setLevel(logging.WARNING)\n\n\ndef get_logger(name: str) -> logging.Logger:\n    \"\"\"Get a logger instance.\"\"\"\n    return logging.getLogger(f\"ai_configurator.{name}\")\n\n\nclass LoggerMixin:\n    \"\"\"Mixin class to add logging capabilities to other classes.\"\"\"\n    \n    @property\n    def logger(self) -> logging.Logger:\n        \"\"\"Get logger for this class.\"\"\"\n        return get_logger(self.__class__.__name__.lower())",
                "command": "create"
              },
              "orig_args": {
                "summary": "Create logging utility module",
                "path": "~/dev/ai-configurator/src/ai_configurator/utils/logging.py",
                "file_text": "\"\"\"Logging configuration and utilities.\"\"\"\n\nimport logging\nimport sys\nfrom pathlib import Path\nfrom typing import Optional\n\nfrom rich.console import Console\nfrom rich.logging import RichHandler\n\nconsole = Console()\n\n\ndef setup_logging(level: str = \"INFO\", log_file: Optional[Path] = None) -> None:\n    \"\"\"Setup logging configuration with Rich handler.\"\"\"\n    \n    # Convert string level to logging constant\n    numeric_level = getattr(logging, level.upper(), logging.INFO)\n    \n    # Create logger\n    logger = logging.getLogger(\"ai_configurator\")\n    logger.setLevel(numeric_level)\n    \n    # Clear any existing handlers\n    logger.handlers.clear()\n    \n    # Create Rich handler for console output\n    rich_handler = RichHandler(\n        console=console,\n        show_time=False,\n        show_path=False,\n        markup=True,\n        rich_tracebacks=True\n    )\n    rich_handler.setLevel(numeric_level)\n    \n    # Create formatter\n    formatter = logging.Formatter(\n        fmt=\"%(message)s\",\n        datefmt=\"[%X]\"\n    )\n    rich_handler.setFormatter(formatter)\n    \n    # Add handler to logger\n    logger.addHandler(rich_handler)\n    \n    # Add file handler if log_file is specified\n    if log_file:\n        log_file.parent.mkdir(parents=True, exist_ok=True)\n        file_handler = logging.FileHandler(log_file)\n        file_handler.setLevel(logging.DEBUG)  # Always log everything to file\n        \n        file_formatter = logging.Formatter(\n            fmt=\"%(asctime)s - %(name)s - %(levelname)s - %(message)s\",\n            datefmt=\"%Y-%m-%d %H:%M:%S\"\n        )\n        file_handler.setFormatter(file_formatter)\n        logger.addHandler(file_handler)\n    \n    # Set root logger level to prevent other libraries from being too verbose\n    logging.getLogger().setLevel(logging.WARNING)\n\n\ndef get_logger(name: str) -> logging.Logger:\n    \"\"\"Get a logger instance.\"\"\"\n    return logging.getLogger(f\"ai_configurator.{name}\")\n\n\nclass LoggerMixin:\n    \"\"\"Mixin class to add logging capabilities to other classes.\"\"\"\n    \n    @property\n    def logger(self) -> logging.Logger:\n        \"\"\"Get logger for this class.\"\"\"\n        return get_logger(self.__class__.__name__.lower())",
                "command": "create"
              }
            }
          ]
        }
      }
    ],
    [
      {
        "additional_context": "",
        "env_context": {
          "env_state": {
            "operating_system": "macos",
            "current_working_directory": "/Users/janossch/dev/linux-configurations/.aws/amazonq",
            "environment_variables": []
          }
        },
        "content": {
          "ToolUseResults": {
            "tool_use_results": [
              {
                "tool_use_id": "tooluse_ar81lK7FS9-DJJWG7pITlw",
                "content": [
                  {
                    "Text": ""
                  }
                ],
                "status": "Success"
              }
            ]
          }
        },
        "images": null
      },
      {
        "ToolUse": {
          "message_id": "f33c77e7-d074-4751-a0bb-840ed39c4c01",
          "content": "Let's create the core module init files:",
          "tool_uses": [
            {
              "id": "tooluse_qRrH8GvhQ1a0KlrIQ7SuDw",
              "name": "fs_write",
              "orig_name": "fs_write",
              "args": {
                "summary": "Create core module init files",
                "path": "~/dev/ai-configurator/src/ai_configurator/core/__init__.py",
                "file_text": "\"\"\"Core functionality for AI Configurator.\"\"\"\n\nfrom .platform import PlatformManager\n\n__all__ = [\"PlatformManager\"]",
                "command": "create"
              },
              "orig_args": {
                "summary": "Create core module init files",
                "path": "~/dev/ai-configurator/src/ai_configurator/core/__init__.py",
                "file_text": "\"\"\"Core functionality for AI Configurator.\"\"\"\n\nfrom .platform import PlatformManager\n\n__all__ = [\"PlatformManager\"]",
                "command": "create"
              }
            }
          ]
        }
      }
    ],
    [
      {
        "additional_context": "",
        "env_context": {
          "env_state": {
            "operating_system": "macos",
            "current_working_directory": "/Users/janossch/dev/linux-configurations/.aws/amazonq",
            "environment_variables": []
          }
        },
        "content": {
          "ToolUseResults": {
            "tool_use_results": [
              {
                "tool_use_id": "tooluse_qRrH8GvhQ1a0KlrIQ7SuDw",
                "content": [
                  {
                    "Text": ""
                  }
                ],
                "status": "Success"
              }
            ]
          }
        },
        "images": null
      },
      {
        "ToolUse": {
          "message_id": "fd0bd51b-36cf-49fb-8ec4-08859fb14791",
          "content": "",
          "tool_uses": [
            {
              "id": "tooluse_w-yBhyBYSb6GnjFof0sqQg",
              "name": "fs_write",
              "orig_name": "fs_write",
              "args": {
                "summary": "Create utils module init file",
                "path": "~/dev/ai-configurator/src/ai_configurator/utils/__init__.py",
                "file_text": "\"\"\"Utility functions and helpers.\"\"\"\n\nfrom .logging import get_logger, setup_logging, LoggerMixin\n\n__all__ = [\"get_logger\", \"setup_logging\", \"LoggerMixin\"]",
                "command": "create"
              },
              "orig_args": {
                "summary": "Create utils module init file",
                "path": "~/dev/ai-configurator/src/ai_configurator/utils/__init__.py",
                "file_text": "\"\"\"Utility functions and helpers.\"\"\"\n\nfrom .logging import get_logger, setup_logging, LoggerMixin\n\n__all__ = [\"get_logger\", \"setup_logging\", \"LoggerMixin\"]",
                "command": "create"
              }
            }
          ]
        }
      }
    ],
    [
      {
        "additional_context": "",
        "env_context": {
          "env_state": {
            "operating_system": "macos",
            "current_working_directory": "/Users/janossch/dev/linux-configurations/.aws/amazonq",
            "environment_variables": []
          }
        },
        "content": {
          "ToolUseResults": {
            "tool_use_results": [
              {
                "tool_use_id": "tooluse_w-yBhyBYSb6GnjFof0sqQg",
                "content": [
                  {
                    "Text": ""
                  }
                ],
                "status": "Success"
              }
            ]
          }
        },
        "images": null
      },
      {
        "ToolUse": {
          "message_id": "46b84457-6285-4476-8ea8-a50719ebe27d",
          "content": "",
          "tool_uses": [
            {
              "id": "tooluse_nwj1X-dUQFK3RQOhNNHSQQ",
              "name": "fs_write",
              "orig_name": "fs_write",
              "args": {
                "summary": "Create commands module init file",
                "path": "~/dev/ai-configurator/src/ai_configurator/commands/__init__.py",
                "file_text": "\"\"\"CLI command implementations.\"\"\"\n\n# Commands will be added here as we implement them",
                "command": "create"
              },
              "orig_args": {
                "summary": "Create commands module init file",
                "path": "~/dev/ai-configurator/src/ai_configurator/commands/__init__.py",
                "file_text": "\"\"\"CLI command implementations.\"\"\"\n\n# Commands will be added here as we implement them",
                "command": "create"
              }
            }
          ]
        }
      }
    ],
    [
      {
        "additional_context": "",
        "env_context": {
          "env_state": {
            "operating_system": "macos",
            "current_working_directory": "/Users/janossch/dev/linux-configurations/.aws/amazonq",
            "environment_variables": []
          }
        },
        "content": {
          "ToolUseResults": {
            "tool_use_results": [
              {
                "tool_use_id": "tooluse_nwj1X-dUQFK3RQOhNNHSQQ",
                "content": [
                  {
                    "Text": ""
                  }
                ],
                "status": "Success"
              }
            ]
          }
        },
        "images": null
      },
      {
        "ToolUse": {
          "message_id": "62bed903-69a5-45cb-8451-67c4cbb32d78",
          "content": "Now let's create a virtual environment and test our basic CLI:",
          "tool_uses": [
            {
              "id": "tooluse_rAfFp_HgRmmXuyguXAkYHw",
              "name": "execute_bash",
              "orig_name": "execute_bash",
              "args": {
                "summary": "Create virtual environment and install dependencies",
                "command": "cd ~/dev/ai-configurator && python -m venv venv"
              },
              "orig_args": {
                "summary": "Create virtual environment and install dependencies",
                "command": "cd ~/dev/ai-configurator && python -m venv venv"
              }
            }
          ]
        }
      }
    ],
    [
      {
        "additional_context": "",
        "env_context": {
          "env_state": {
            "operating_system": "macos",
            "current_working_directory": "/Users/janossch/dev/linux-configurations/.aws/amazonq",
            "environment_variables": []
          }
        },
        "content": {
          "ToolUseResults": {
            "tool_use_results": [
              {
                "tool_use_id": "tooluse_rAfFp_HgRmmXuyguXAkYHw",
                "content": [
                  {
                    "Json": {
                      "exit_status": "0",
                      "stdout": "",
                      "stderr": ""
                    }
                  }
                ],
                "status": "Success"
              }
            ]
          }
        },
        "images": null
      },
      {
        "ToolUse": {
          "message_id": "0de62834-c7fa-4e6a-aaf9-f6409ab60283",
          "content": "",
          "tool_uses": [
            {
              "id": "tooluse_SDuS3f6_TLiOj7N1i4mzkA",
              "name": "execute_bash",
              "orig_name": "execute_bash",
              "args": {
                "summary": "Activate virtual environment and install package in development mode",
                "command": "cd ~/dev/ai-configurator && source venv/bin/activate && pip install -e ."
              },
              "orig_args": {
                "summary": "Activate virtual environment and install package in development mode",
                "command": "cd ~/dev/ai-configurator && source venv/bin/activate && pip install -e ."
              }
            }
          ]
        }
      }
    ],
    [
      {
        "additional_context": "",
        "env_context": {
          "env_state": {
            "operating_system": "macos",
            "current_working_directory": "/Users/janossch/dev/linux-configurations/.aws/amazonq",
            "environment_variables": []
          }
        },
        "content": {
          "ToolUseResults": {
            "tool_use_results": [
              {
                "tool_use_id": "tooluse_SDuS3f6_TLiOj7N1i4mzkA",
                "content": [
                  {
                    "Json": {
                      "exit_status": "1",
                      "stdout": "Obtaining file:///Users/janossch/dev/ai-configurator\n  Installing build dependencies: started\n  Installing build dependencies: finished with status 'done'\n  Checking if build backend supports build_editable: started\n  Checking if build backend supports build_editable: finished with status 'done'\n  Getting requirements to build editable: started\n  Getting requirements to build editable: finished with status 'done'\n  Installing backend dependencies: started\n  Installing backend dependencies: finished with status 'done'\n  Preparing editable metadata (pyproject.toml): started\n  Preparing editable metadata (pyproject.toml): finished with status 'error'",
                      "stderr": "  error: subprocess-exited-with-error\n  \n  × Preparing editable metadata (pyproject.toml) did not run successfully.\n  │ exit code: 1\n  ╰─> [29 lines of output]\n      Traceback (most recent call last):\n        File \"/Users/janossch/dev/ai-configurator/venv/lib/python3.12/site-packages/pip/_vendor/pyproject_hooks/_in_process/_in_process.py\", line 167, in prepare_metadata_for_build_editable\n          hook = backend.prepare_metadata_for_build_editable\n                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n      AttributeError: module 'hatchling.build' has no attribute 'prepare_metadata_for_build_editable'\n      \n      During handling of the above exception, another exception occurred:\n      \n      Traceback (most recent call last):\n        File \"/Users/janossch/dev/ai-configurator/venv/lib/python3.12/site-packages/pip/_vendor/pyproject_hooks/_in_process/_in_process.py\", line 353, in <module>\n          main()\n        File \"/Users/janossch/dev/ai-configurator/venv/lib/python3.12/site-packages/pip/_vendor/pyproject_hooks/_in_process/_in_process.py\", line 335, in main\n          json_out['return_val'] = hook(**hook_input['kwargs'])\n                                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n        File \"/Users/janossch/dev/ai-configurator/venv/lib/python3.12/site-packages/pip/_vendor/pyproject_hooks/_in_process/_in_process.py\", line 176, in prepare_metadata_for_build_editable\n          whl_basename = build_hook(metadata_directory, config_settings)\n                         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n        File \"/private/var/folders/z2/c1dttf3n3ndb9grc18m1dgrxw9h5qb/T/pip-build-env-sld2etc0/overlay/lib/python3.12/site-packages/hatchling/build.py\", line 83, in build_editable\n          return os.path.basename(next(builder.build(directory=wheel_directory, versions=['editable'])))\n                                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n        File \"/private/var/folders/z2/c1dttf3n3ndb9grc18m1dgrxw9h5qb/T/pip-build-env-sld2etc0/overlay/lib/python3.12/site-packages/hatchling/builders/plugin/interface.py\", line 90, in build\n          self.metadata.validate_fields()\n        File \"/private/var/folders/z2/c1dttf3n3ndb9grc18m1dgrxw9h5qb/T/pip-build-env-sld2etc0/overlay/lib/python3.12/site-packages/hatchling/metadata/core.py\", line 266, in validate_fields\n          self.core.validate_fields()\n        File \"/private/var/folders/z2/c1dttf3n3ndb9grc18m1dgrxw9h5qb/T/pip-build-env-sld2etc0/overlay/lib/python3.12/site-packages/hatchling/metadata/core.py\", line 1366, in validate_fields\n          getattr(self, attribute)\n        File \"/private/var/folders/z2/c1dttf3n3ndb9grc18m1dgrxw9h5qb/T/pip-build-env-sld2etc0/overlay/lib/python3.12/site-packages/hatchling/metadata/core.py\", line 991, in classifiers\n          raise ValueError(message)\n      ValueError: Unknown classifier in field `project.classifiers`: Topic :: Software Development :: Tools\n      [end of output]\n  \n  note: This error originates from a subprocess, and is likely not a problem with pip.\nerror: metadata-generation-failed\n\n× Encountered error while generating package metadata.\n╰─> See above for output.\n\nnote: This is an issue with the package mentioned above, not pip.\nhint: See above for details.\n\n[notice] A new release of pip is available: 24.0 -> 25.1.1\n[notice] To update, run: pip install --upgrade pip"
                    }
                  }
                ],
                "status": "Success"
              }
            ]
          }
        },
        "images": null
      },
      {
        "ToolUse": {
          "message_id": "be9d11aa-cc79-4adf-b5b3-1a8e9f919889",
          "content": "Let me fix the pyproject.toml file - there's an issue with the classifier:",
          "tool_uses": [
            {
              "id": "tooluse_wL8trS-rTPO3lsDEY0AYEw",
              "name": "fs_write",
              "orig_name": "fs_write",
              "args": {
                "summary": "Fix pyproject.toml with correct classifiers",
                "path": "~/dev/ai-configurator/pyproject.toml",
                "file_text": "[build-system]\nrequires = [\"hatchling\"]\nbuild-backend = \"hatchling.build\"\n\n[project]\nname = \"ai-configurator\"\nversion = \"0.1.0\"\ndescription = \"Cross-platform configuration manager for Amazon Q CLI\"\nreadme = \"README.md\"\nrequires-python = \">=3.8\"\nlicense = \"MIT\"\nauthors = [\n    { name = \"AI Configurator Team\" },\n]\nkeywords = [\"amazon-q\", \"cli\", \"configuration\", \"ai\", \"mcp\"]\nclassifiers = [\n    \"Development Status :: 3 - Alpha\",\n    \"Intended Audience :: Developers\",\n    \"License :: OSI Approved :: MIT License\",\n    \"Operating System :: OS Independent\",\n    \"Programming Language :: Python :: 3\",\n    \"Programming Language :: Python :: 3.8\",\n    \"Programming Language :: Python :: 3.9\",\n    \"Programming Language :: Python :: 3.10\",\n    \"Programming Language :: Python :: 3.11\",\n    \"Programming Language :: Python :: 3.12\",\n    \"Topic :: Software Development\",\n    \"Topic :: System :: Installation/Setup\",\n]\n\ndependencies = [\n    \"click>=8.0.0\",\n    \"pydantic>=2.0.0\",\n    \"rich>=13.0.0\",\n    \"pyyaml>=6.0.0\",\n    \"packaging>=21.0.0\",\n    \"platformdirs>=3.0.0\",\n]\n\n[project.optional-dependencies]\ndev = [\n    \"pytest>=7.0.0\",\n    \"pytest-cov>=4.0.0\",\n    \"black>=23.0.0\",\n    \"isort>=5.0.0\",\n    \"flake8>=6.0.0\",\n    \"mypy>=1.0.0\",\n    \"pre-commit>=3.0.0\",\n]\n\n[project.urls]\nHomepage = \"https://github.com/your-org/ai-configurator\"\nDocumentation = \"https://ai-configurator.readthedocs.io\"\nRepository = \"https://github.com/your-org/ai-configurator.git\"\n\"Bug Tracker\" = \"https://github.com/your-org/ai-configurator/issues\"\n\n[project.scripts]\nai-config = \"ai_configurator.cli:main\"\n\n[tool.hatch.build.targets.wheel]\npackages = [\"src/ai_configurator\"]\n\n[tool.hatch.build.targets.sdist]\ninclude = [\n    \"/src\",\n    \"/configs\",\n    \"/contexts\",\n    \"/hooks\",\n    \"/templates\",\n]\n\n[tool.black]\nline-length = 88\ntarget-version = ['py38']\ninclude = '\\.pyi?$'\n\n[tool.isort]\nprofile = \"black\"\nmulti_line_output = 3\n\n[tool.mypy]\npython_version = \"3.8\"\nwarn_return_any = true\nwarn_unused_configs = true\ndisallow_untyped_defs = true\n\n[tool.pytest.ini_options]\ntestpaths = [\"tests\"]\npython_files = [\"test_*.py\"]\npython_classes = [\"Test*\"]\npython_functions = [\"test_*\"]\naddopts = \"--cov=ai_configurator --cov-report=term-missing\"",
                "command": "str_replace",
                "old_str": "[build-system]\nrequires = [\"hatchling\"]\nbuild-backend = \"hatchling.build\"\n\n[project]\nname = \"ai-configurator\"\nversion = \"0.1.0\"\ndescription = \"Cross-platform configuration manager for Amazon Q CLI\"\nreadme = \"README.md\"\nrequires-python = \">=3.8\"\nlicense = \"MIT\"\nauthors = [\n    { name = \"AI Configurator Team\" },\n]\nkeywords = [\"amazon-q\", \"cli\", \"configuration\", \"ai\", \"mcp\"]\nclassifiers = [\n    \"Development Status :: 3 - Alpha\",\n    \"Intended Audience :: Developers\",\n    \"License :: OSI Approved :: MIT License\",\n    \"Operating System :: OS Independent\",\n    \"Programming Language :: Python :: 3\",\n    \"Programming Language :: Python :: 3.8\",\n    \"Programming Language :: Python :: 3.9\",\n    \"Programming Language :: Python :: 3.10\",\n    \"Programming Language :: Python :: 3.11\",\n    \"Programming Language :: Python :: 3.12\",\n    \"Topic :: Software Development :: Tools\",\n    \"Topic :: System :: Installation/Setup\",\n]",
                "new_str": "[build-system]\nrequires = [\"hatchling\"]\nbuild-backend = \"hatchling.build\"\n\n[project]\nname = \"ai-configurator\"\nversion = \"0.1.0\"\ndescription = \"Cross-platform configuration manager for Amazon Q CLI\"\nreadme = \"README.md\"\nrequires-python = \">=3.8\"\nlicense = \"MIT\"\nauthors = [\n    { name = \"AI Configurator Team\" },\n]\nkeywords = [\"amazon-q\", \"cli\", \"configuration\", \"ai\", \"mcp\"]\nclassifiers = [\n    \"Development Status :: 3 - Alpha\",\n    \"Intended Audience :: Developers\",\n    \"License :: OSI Approved :: MIT License\",\n    \"Operating System :: OS Independent\",\n    \"Programming Language :: Python :: 3\",\n    \"Programming Language :: Python :: 3.8\",\n    \"Programming Language :: Python :: 3.9\",\n    \"Programming Language :: Python :: 3.10\",\n    \"Programming Language :: Python :: 3.11\",\n    \"Programming Language :: Python :: 3.12\",\n    \"Topic :: Software Development\",\n    \"Topic :: System :: Installation/Setup\",\n]"
              },
              "orig_args": {
                "summary": "Fix pyproject.toml with correct classifiers",
                "path": "~/dev/ai-configurator/pyproject.toml",
                "file_text": "[build-system]\nrequires = [\"hatchling\"]\nbuild-backend = \"hatchling.build\"\n\n[project]\nname = \"ai-configurator\"\nversion = \"0.1.0\"\ndescription = \"Cross-platform configuration manager for Amazon Q CLI\"\nreadme = \"README.md\"\nrequires-python = \">=3.8\"\nlicense = \"MIT\"\nauthors = [\n    { name = \"AI Configurator Team\" },\n]\nkeywords = [\"amazon-q\", \"cli\", \"configuration\", \"ai\", \"mcp\"]\nclassifiers = [\n    \"Development Status :: 3 - Alpha\",\n    \"Intended Audience :: Developers\",\n    \"License :: OSI Approved :: MIT License\",\n    \"Operating System :: OS Independent\",\n    \"Programming Language :: Python :: 3\",\n    \"Programming Language :: Python :: 3.8\",\n    \"Programming Language :: Python :: 3.9\",\n    \"Programming Language :: Python :: 3.10\",\n    \"Programming Language :: Python :: 3.11\",\n    \"Programming Language :: Python :: 3.12\",\n    \"Topic :: Software Development\",\n    \"Topic :: System :: Installation/Setup\",\n]\n\ndependencies = [\n    \"click>=8.0.0\",\n    \"pydantic>=2.0.0\",\n    \"rich>=13.0.0\",\n    \"pyyaml>=6.0.0\",\n    \"packaging>=21.0.0\",\n    \"platformdirs>=3.0.0\",\n]\n\n[project.optional-dependencies]\ndev = [\n    \"pytest>=7.0.0\",\n    \"pytest-cov>=4.0.0\",\n    \"black>=23.0.0\",\n    \"isort>=5.0.0\",\n    \"flake8>=6.0.0\",\n    \"mypy>=1.0.0\",\n    \"pre-commit>=3.0.0\",\n]\n\n[project.urls]\nHomepage = \"https://github.com/your-org/ai-configurator\"\nDocumentation = \"https://ai-configurator.readthedocs.io\"\nRepository = \"https://github.com/your-org/ai-configurator.git\"\n\"Bug Tracker\" = \"https://github.com/your-org/ai-configurator/issues\"\n\n[project.scripts]\nai-config = \"ai_configurator.cli:main\"\n\n[tool.hatch.build.targets.wheel]\npackages = [\"src/ai_configurator\"]\n\n[tool.hatch.build.targets.sdist]\ninclude = [\n    \"/src\",\n    \"/configs\",\n    \"/contexts\",\n    \"/hooks\",\n    \"/templates\",\n]\n\n[tool.black]\nline-length = 88\ntarget-version = ['py38']\ninclude = '\\.pyi?$'\n\n[tool.isort]\nprofile = \"black\"\nmulti_line_output = 3\n\n[tool.mypy]\npython_version = \"3.8\"\nwarn_return_any = true\nwarn_unused_configs = true\ndisallow_untyped_defs = true\n\n[tool.pytest.ini_options]\ntestpaths = [\"tests\"]\npython_files = [\"test_*.py\"]\npython_classes = [\"Test*\"]\npython_functions = [\"test_*\"]\naddopts = \"--cov=ai_configurator --cov-report=term-missing\"",
                "command": "str_replace",
                "old_str": "[build-system]\nrequires = [\"hatchling\"]\nbuild-backend = \"hatchling.build\"\n\n[project]\nname = \"ai-configurator\"\nversion = \"0.1.0\"\ndescription = \"Cross-platform configuration manager for Amazon Q CLI\"\nreadme = \"README.md\"\nrequires-python = \">=3.8\"\nlicense = \"MIT\"\nauthors = [\n    { name = \"AI Configurator Team\" },\n]\nkeywords = [\"amazon-q\", \"cli\", \"configuration\", \"ai\", \"mcp\"]\nclassifiers = [\n    \"Development Status :: 3 - Alpha\",\n    \"Intended Audience :: Developers\",\n    \"License :: OSI Approved :: MIT License\",\n    \"Operating System :: OS Independent\",\n    \"Programming Language :: Python :: 3\",\n    \"Programming Language :: Python :: 3.8\",\n    \"Programming Language :: Python :: 3.9\",\n    \"Programming Language :: Python :: 3.10\",\n    \"Programming Language :: Python :: 3.11\",\n    \"Programming Language :: Python :: 3.12\",\n    \"Topic :: Software Development :: Tools\",\n    \"Topic :: System :: Installation/Setup\",\n]",
                "new_str": "[build-system]\nrequires = [\"hatchling\"]\nbuild-backend = \"hatchling.build\"\n\n[project]\nname = \"ai-configurator\"\nversion = \"0.1.0\"\ndescription = \"Cross-platform configuration manager for Amazon Q CLI\"\nreadme = \"README.md\"\nrequires-python = \">=3.8\"\nlicense = \"MIT\"\nauthors = [\n    { name = \"AI Configurator Team\" },\n]\nkeywords = [\"amazon-q\", \"cli\", \"configuration\", \"ai\", \"mcp\"]\nclassifiers = [\n    \"Development Status :: 3 - Alpha\",\n    \"Intended Audience :: Developers\",\n    \"License :: OSI Approved :: MIT License\",\n    \"Operating System :: OS Independent\",\n    \"Programming Language :: Python :: 3\",\n    \"Programming Language :: Python :: 3.8\",\n    \"Programming Language :: Python :: 3.9\",\n    \"Programming Language :: Python :: 3.10\",\n    \"Programming Language :: Python :: 3.11\",\n    \"Programming Language :: Python :: 3.12\",\n    \"Topic :: Software Development\",\n    \"Topic :: System :: Installation/Setup\",\n]"
              }
            }
          ]
        }
      }
    ],
    [
      {
        "additional_context": "",
        "env_context": {
          "env_state": {
            "operating_system": "macos",
            "current_working_directory": "/Users/janossch/dev/linux-configurations/.aws/amazonq",
            "environment_variables": []
          }
        },
        "content": {
          "ToolUseResults": {
            "tool_use_results": [
              {
                "tool_use_id": "tooluse_wL8trS-rTPO3lsDEY0AYEw",
                "content": [
                  {
                    "Text": ""
                  }
                ],
                "status": "Success"
              }
            ]
          }
        },
        "images": null
      },
      {
        "ToolUse": {
          "message_id": "f06ea36d-0a7f-49ce-ab9c-bae7b9b606ee",
          "content": "Now let's try installing again:",
          "tool_uses": [
            {
              "id": "tooluse_fH9rnMm3SGytTh8LqBQOag",
              "name": "execute_bash",
              "orig_name": "execute_bash",
              "args": {
                "summary": "Install package in development mode",
                "command": "cd ~/dev/ai-configurator && source venv/bin/activate && pip install -e ."
              },
              "orig_args": {
                "summary": "Install package in development mode",
                "command": "cd ~/dev/ai-configurator && source venv/bin/activate && pip install -e ."
              }
            }
          ]
        }
      }
    ],
    [
      {
        "additional_context": "",
        "env_context": {
          "env_state": {
            "operating_system": "macos",
            "current_working_directory": "/Users/janossch/dev/linux-configurations/.aws/amazonq",
            "environment_variables": []
          }
        },
        "content": {
          "ToolUseResults": {
            "tool_use_results": [
              {
                "tool_use_id": "tooluse_fH9rnMm3SGytTh8LqBQOag",
                "content": [
                  {
                    "Json": {
                      "exit_status": "0",
                      "stdout": "Obtaining file:///Users/janossch/dev/ai-configurator\n  Installing build dependencies: started\n  Installing build dependencies: finished with status 'done'\n  Checking if build backend supports build_editable: started\n  Checking if build backend supports build_editable: finished with status 'done'\n  Getting requirements to build editable: started\n  Getting requirements to build editable: finished with status 'done'\n  Installing backend dependencies: started\n  Installing backend dependencies: finished with status 'done'\n  Preparing editable metadata (pyproject.toml): started\n  Preparing editable metadata (pyproject.toml): finished with status 'done'\nCollecting click>=8.0.0 (from ai-configurator==0.1.0)\n  Using cached click-8.2.1-py3-none-any.whl.metadata (2.5 kB)\nCollecting packaging>=21.0.0 (from ai-configurator==0.1.0)\n  Using cached packaging-25.0-py3-none-any.whl.metadata (3.3 kB)\nCollecting platformdirs>=3.0.0 (from ai-configurator==0.1.0)\n  Downloading platformdirs-4.3.8-py3-none-any.whl.metadata (12 kB)\nCollecting pydantic>=2.0.0 (from ai-configurator==0.1.0)\n  Using cached pydantic-2.11.7-py3-none-any.whl.metadata (67 kB)\nCollecting pyyaml>=6.0.0 (from ai-configurator==0.1.0)\n  Using cached PyYAML-6.0.2-cp312-cp312-macosx_11_0_arm64.whl.metadata (2.1 kB)\nCollecting rich>=13.0.0 (from ai-configurator==0.1.0)\n  Downloading rich-14.1.0-py3-none-any.whl.metadata (18 kB)\nCollecting annotated-types>=0.6.0 (from pydantic>=2.0.0->ai-configurator==0.1.0)\n  Using cached annotated_types-0.7.0-py3-none-any.whl.metadata (15 kB)\nCollecting pydantic-core==2.33.2 (from pydantic>=2.0.0->ai-configurator==0.1.0)\n  Using cached pydantic_core-2.33.2-cp312-cp312-macosx_11_0_arm64.whl.metadata (6.8 kB)\nCollecting typing-extensions>=4.12.2 (from pydantic>=2.0.0->ai-configurator==0.1.0)\n  Downloading typing_extensions-4.14.1-py3-none-any.whl.metadata (3.0 kB)\nCollecting typing-inspection>=0.4.0 (from pydantic>=2.0.0->ai-configurator==0.1.0)\n  Using cached typing_inspection-0.4.1-py3-none-any.whl.metadata (2.6 kB)\nCollecting markdown-it-py>=2.2.0 (from rich>=13.0.0->ai-configurator==0.1.0)\n  Using cached markdown_it_py-3.0.0-py3-none-any.whl.metadata (6.9 kB)\nCollecting pygments<3.0.0,>=2.13.0 (from rich>=13.0.0->ai-configurator==0.1.0)\n  Using cached pygments-2.19.2-py3-none-any.whl.metadata (2.5 kB)\nCollecting mdurl~=0.1 (from markdown-it-py>=2.2.0->rich>=13.0.0->ai-configurator==0.1.0)\n  Using cached mdurl-0.1.2-py3-none-any.whl.metadata (1.6 kB)\nUsing cached click-8.2.1-py3-none-any.whl (102 kB)\nUsing cached packaging-25.0-py3-none-any.whl (66 kB)\nDownloading platformdirs-4.3.8-py3-none-any.whl (18 kB)\nUsing cached pydantic-2.11.7-py3-none-any.whl (444 kB)\nUsing cached pydantic_core-2.33.2-cp312-cp312-macosx_11_0_arm64.whl (1.8 MB)\nUsing cached PyYAML-6.0.2-cp312-cp312-macosx_11_0_arm64.whl (173 kB)\nDownloading rich-14.1.0-py3-none-any.whl (243 kB)\n   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 243.4/243.4 kB 8.2 MB/s eta 0:00:00\nUsing cached annotated_types-0.7.0-py3-none-any.whl (13 kB)\nUsing cached markdown_it_py-3.0.0-py3-none-any.whl (87 kB)\nUsing cached pygments-2.19.2-py3-none-any.whl (1.2 MB)\nDownloading typing_extensions-4.14.1-py3-none-any.whl (43 kB)\n   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 43.9/43.9 kB 3.2 MB/s eta 0:00:00\nUsing cached typing_inspection-0.4.1-py3-none-any.whl (14 kB)\nUsing cached mdurl-0.1.2-py3-none-any.whl (10.0 kB)\nBuilding wheels for collected packages: ai-configurator\n  Building editable for ai-configurator (pyproject.toml): started\n  Building editable for ai-configurator (pyproject.toml): finished with status 'done'\n  Created wheel for ai-configurator: filename=ai_configurator-0.1.0-py3-none-any.whl size=3118 sha256=419a273ebbb477d6583b70afe7d4d1fb379c6a648de511d9e2c309e3706cc836\n  Stored in directory: /private/var/folders/z2/c1dttf3n3ndb9grc18m1dgrxw9h5qb/T/pip-ephem-wheel-cache-j4rmsqrc/wheels/5a/ec/cc/e3cfc9f5bf3769abbfc9cb9ce1c2153cc4b1e6851ffad9ebbf\nSuccessfully built ai-configurator\nInstalling collected packages: typing-extensions, pyyaml, pygments, platformdirs, packaging, mdurl, click, annotated-types, typing-inspection, pydantic-core, markdown-it-py, rich, pydantic, ai-configurator\nSuccessfully installed ai-configurator-0.1.0 annotated-types-0.7.0 click-8.2.1 markdown-it-py-3.0.0 mdurl-0.1.2 packaging-25.0 platformdirs-4.3.8 pydantic-2.11.7 pydantic-core-2.33.2 pygments-2.19.2 pyyaml-6.0.2 rich-14.1.0 typing-extensions-4.14.1 typing-inspection-0.4.1",
                      "stderr": "\n[notice] A new release of pip is available: 24.0 -> 25.1.1\n[notice] To update, run: pip install --upgrade pip"
                    }
                  }
                ],
                "status": "Success"
              }
            ]
          }
        },
        "images": null
      },
      {
        "ToolUse": {
          "message_id": "31d0ae8f-f7c4-4135-bb47-a84bdd327f9a",
          "content": "Great! Now let's test our CLI:",
          "tool_uses": [
            {
              "id": "tooluse_J_62_ONzTVeOLetry6G33A",
              "name": "execute_bash",
              "orig_name": "execute_bash",
              "args": {
                "summary": "Test the basic CLI functionality",
                "command": "cd ~/dev/ai-configurator && source venv/bin/activate && ai-config --help"
              },
              "orig_args": {
                "summary": "Test the basic CLI functionality",
                "command": "cd ~/dev/ai-configurator && source venv/bin/activate && ai-config --help"
              }
            }
          ]
        }
      }
    ],
    [
      {
        "additional_context": "",
        "env_context": {
          "env_state": {
            "operating_system": "macos",
            "current_working_directory": "/Users/janossch/dev/linux-configurations/.aws/amazonq",
            "environment_variables": []
          }
        },
        "content": {
          "ToolUseResults": {
            "tool_use_results": [
              {
                "tool_use_id": "tooluse_J_62_ONzTVeOLetry6G33A",
                "content": [
                  {
                    "Json": {
                      "exit_status": "0",
                      "stdout": "Usage: ai-config [OPTIONS] COMMAND [ARGS]...\n\n  AI Configurator - Cross-platform configuration manager for Amazon Q CLI.\n\nOptions:\n  --version      Show the version and exit.\n  -v, --verbose  Enable verbose output\n  -q, --quiet    Suppress non-error output\n  --help         Show this message and exit.\n\nCommands:\n  backup    Backup current configuration.\n  install   Install Amazon Q CLI configuration.\n  profile   Manage configuration profiles.\n  restore   Restore configuration from backup.\n  status    Show current configuration status.\n  update    Update existing Amazon Q CLI configuration.\n  validate  Validate current configuration.",
                      "stderr": ""
                    }
                  }
                ],
                "status": "Success"
              }
            ]
          }
        },
        "images": null
      },
      {
        "ToolUse": {
          "message_id": "67c7cfd3-0351-4f8d-8aa5-5d1a87c284b5",
          "content": "",
          "tool_uses": [
            {
              "id": "tooluse_xD70ynYfSKq2PYkyU9T4UA",
              "name": "execute_bash",
              "orig_name": "execute_bash",
              "args": {
                "summary": "Test the status command",
                "command": "cd ~/dev/ai-configurator && source venv/bin/activate && ai-config status"
              },
              "orig_args": {
                "summary": "Test the status command",
                "command": "cd ~/dev/ai-configurator && source venv/bin/activate && ai-config status"
              }
            }
          ]
        }
      }
    ],
    [
      {
        "additional_context": "",
        "env_context": {
          "env_state": {
            "operating_system": "macos",
            "current_working_directory": "/Users/janossch/dev/linux-configurations/.aws/amazonq",
            "environment_variables": []
          }
        },
        "content": {
          "ToolUseResults": {
            "tool_use_results": [
              {
                "tool_use_id": "tooluse_xD70ynYfSKq2PYkyU9T4UA",
                "content": [
                  {
                    "Json": {
                      "exit_status": "0",
                      "stdout": "╭─────────── AI Configurator Status ────────────╮\n│ Platform: Darwin                              │\n│ Amazon Q Config: /Users/janossch/.aws/amazonq │\n│ Version: 0.1.0                                │\n╰───────────────────────────────────────────────╯",
                      "stderr": ""
                    }
                  }
                ],
                "status": "Success"
              }
            ]
          }
        },
        "images": null
      },
      {
        "ToolUse": {
          "message_id": "3c7df524-2bae-49e6-a557-94d9e28a3cb0",
          "content": "",
          "tool_uses": [
            {
              "id": "tooluse_cRzqQZRzRt-ArbUVxh3vPQ",
              "name": "execute_bash",
              "orig_name": "execute_bash",
              "args": {
                "summary": "Test the validate command",
                "command": "cd ~/dev/ai-configurator && source venv/bin/activate && ai-config validate"
              },
              "orig_args": {
                "summary": "Test the validate command",
                "command": "cd ~/dev/ai-configurator && source venv/bin/activate && ai-config validate"
              }
            }
          ]
        }
      }
    ],
    [
      {
        "additional_context": "",
        "env_context": {
          "env_state": {
            "operating_system": "macos",
            "current_working_directory": "/Users/janossch/dev/linux-configurations/.aws/amazonq",
            "environment_variables": []
          }
        },
        "content": {
          "ToolUseResults": {
            "tool_use_results": [
              {
                "tool_use_id": "tooluse_cRzqQZRzRt-ArbUVxh3vPQ",
                "content": [
                  {
                    "Json": {
                      "exit_status": "0",
                      "stdout": "Validating Amazon Q CLI Configuration\n\n✅ Amazon Q CLI: Found\n✅ Config Directory: /Users/janossch/.aws/amazonq\nFull validation functionality coming soon!",
                      "stderr": ""
                    }
                  }
                ],
                "status": "Success"
              }
            ]
          }
        },
        "images": null
      },
      {
        "ToolUse": {
          "message_id": "62262021-d5bd-40f8-946b-f4e4e107112e",
          "content": "Perfect! Our basic CLI is working. Let's update our task list to reflect our progress:",
          "tool_uses": [
            {
              "id": "tooluse_IlKoQHoJRUeljaCds2Nnkw",
              "name": "fs_write",
              "orig_name": "fs_write",
              "args": {
                "summary": "Update task list with completed items",
                "path": "~/dev/ai-configurator/TASKS.md",
                "old_str": "## Phase 1: Core Foundation ⏳\n- [ ] **Project Setup**\n  - [ ] Initialize Python project structure\n  - [ ] Setup pyproject.toml with dependencies\n  - [ ] Create virtual environment\n  - [ ] Setup basic CLI with Click\n  - [ ] Add logging configuration\n\n- [ ] **Platform Detection & Path Management**\n  - [ ] Implement cross-platform path detection for Amazon Q config\n  - [ ] Create platform-specific utilities (Windows/macOS/Linux)\n  - [ ] Handle different shell environments\n\n- [ ] **Configuration Management Core**\n  - [ ] JSON/YAML configuration parser\n  - [ ] Configuration validation system\n  - [ ] Backup and restore functionality\n  - [ ] Safe file operations with rollback",
                "new_str": "## Phase 1: Core Foundation ✅ IN PROGRESS\n- [x] **Project Setup**\n  - [x] Initialize Python project structure\n  - [x] Setup pyproject.toml with dependencies\n  - [x] Create virtual environment\n  - [x] Setup basic CLI with Click\n  - [x] Add logging configuration\n\n- [x] **Platform Detection & Path Management**\n  - [x] Implement cross-platform path detection for Amazon Q config\n  - [x] Create platform-specific utilities (Windows/macOS/Linux)\n  - [x] Handle different shell environments\n\n- [ ] **Configuration Management Core**\n  - [ ] JSON/YAML configuration parser\n  - [ ] Configuration validation system\n  - [ ] Backup and restore functionality\n  - [ ] Safe file operations with rollback",
                "command": "str_replace"
              },
              "orig_args": {
                "summary": "Update task list with completed items",
                "path": "~/dev/ai-configurator/TASKS.md",
                "old_str": "## Phase 1: Core Foundation ⏳\n- [ ] **Project Setup**\n  - [ ] Initialize Python project structure\n  - [ ] Setup pyproject.toml with dependencies\n  - [ ] Create virtual environment\n  - [ ] Setup basic CLI with Click\n  - [ ] Add logging configuration\n\n- [ ] **Platform Detection & Path Management**\n  - [ ] Implement cross-platform path detection for Amazon Q config\n  - [ ] Create platform-specific utilities (Windows/macOS/Linux)\n  - [ ] Handle different shell environments\n\n- [ ] **Configuration Management Core**\n  - [ ] JSON/YAML configuration parser\n  - [ ] Configuration validation system\n  - [ ] Backup and restore functionality\n  - [ ] Safe file operations with rollback",
                "new_str": "## Phase 1: Core Foundation ✅ IN PROGRESS\n- [x] **Project Setup**\n  - [x] Initialize Python project structure\n  - [x] Setup pyproject.toml with dependencies\n  - [x] Create virtual environment\n  - [x] Setup basic CLI with Click\n  - [x] Add logging configuration\n\n- [x] **Platform Detection & Path Management**\n  - [x] Implement cross-platform path detection for Amazon Q config\n  - [x] Create platform-specific utilities (Windows/macOS/Linux)\n  - [x] Handle different shell environments\n\n- [ ] **Configuration Management Core**\n  - [ ] JSON/YAML configuration parser\n  - [ ] Configuration validation system\n  - [ ] Backup and restore functionality\n  - [ ] Safe file operations with rollback",
                "command": "str_replace"
              }
            }
          ]
        }
      }
    ],
    [
      {
        "additional_context": "",
        "env_context": {
          "env_state": {
            "operating_system": "macos",
            "current_working_directory": "/Users/janossch/dev/linux-configurations/.aws/amazonq",
            "environment_variables": []
          }
        },
        "content": {
          "ToolUseResults": {
            "tool_use_results": [
              {
                "tool_use_id": "tooluse_IlKoQHoJRUeljaCds2Nnkw",
                "content": [
                  {
                    "Text": ""
                  }
                ],
                "status": "Success"
              }
            ]
          }
        },
        "images": null
      },
      {
        "ToolUse": {
          "message_id": "73c9e4e8-673a-4398-8d5f-bdcc8bd50db5",
          "content": "",
          "tool_uses": [
            {
              "id": "tooluse_vb-7tEQ2S8WmpCvs5LSAEw",
              "name": "fs_write",
              "orig_name": "fs_write",
              "args": {
                "summary": "Update current status in task list",
                "path": "~/dev/ai-configurator/TASKS.md",
                "new_str": "## Current Status: 🎯 Phase 1 - 60% Complete\n\n## Next Immediate Tasks:\n1. ✅ Setup Python project structure\n2. ✅ Create basic CLI framework\n3. ✅ Implement platform detection\n4. 🔄 Create configuration parser\n5. 🔄 Implement backup/restore functionality\n6. 🔄 Add configuration validation",
                "old_str": "## Current Status: 🎯 Starting Phase 1\n\n## Next Immediate Tasks:\n1. Setup Python project structure\n2. Create basic CLI framework\n3. Implement platform detection\n4. Create configuration parser",
                "command": "str_replace"
              },
              "orig_args": {
                "summary": "Update current status in task list",
                "path": "~/dev/ai-configurator/TASKS.md",
                "new_str": "## Current Status: 🎯 Phase 1 - 60% Complete\n\n## Next Immediate Tasks:\n1. ✅ Setup Python project structure\n2. ✅ Create basic CLI framework\n3. ✅ Implement platform detection\n4. 🔄 Create configuration parser\n5. 🔄 Implement backup/restore functionality\n6. 🔄 Add configuration validation",
                "old_str": "## Current Status: 🎯 Starting Phase 1\n\n## Next Immediate Tasks:\n1. Setup Python project structure\n2. Create basic CLI framework\n3. Implement platform detection\n4. Create configuration parser",
                "command": "str_replace"
              }
            }
          ]
        }
      }
    ],
    [
      {
        "additional_context": "",
        "env_context": {
          "env_state": {
            "operating_system": "macos",
            "current_working_directory": "/Users/janossch/dev/linux-configurations/.aws/amazonq",
            "environment_variables": []
          }
        },
        "content": {
          "ToolUseResults": {
            "tool_use_results": [
              {
                "tool_use_id": "tooluse_vb-7tEQ2S8WmpCvs5LSAEw",
                "content": [
                  {
                    "Text": ""
                  }
                ],
                "status": "Success"
              }
            ]
          }
        },
        "images": null
      },
      {
        "Response": {
          "message_id": "9cea45fd-4dd5-4415-81b3-6ad67637a4ee",
          "content": "Excellent! We've made great progress. Here's what we've accomplished:\n\n## ✅ **What We've Built So Far:**\n\n1. **Complete Project Structure**: Organized Python package with proper module hierarchy\n2. **Cross-Platform CLI**: Working command-line interface using Click framework\n3. **Platform Detection**: Smart detection of Windows/macOS/Linux with appropriate path handling\n4. **Rich UI**: Beautiful terminal output with colors and panels\n5. **Logging System**: Configurable logging with Rich integration\n6. **Package Management**: Proper pyproject.toml with dependencies and development tools\n\n## 🎯 **Current Status:**\n- **Phase 1**: 60% complete\n- **Working CLI**: `ai-config` command is functional\n- **Platform Support**: Detects Amazon Q CLI installation and config paths\n- **Foundation**: Solid base for building advanced features\n\n## 🚀 **Next Steps:**\nThe foundation is solid! Now we can focus on the core functionality:\n\n1. **Configuration Management**: JSON/YAML parsing and validation\n2. **Backup System**: Safe backup and restore operations\n3. **Installation Logic**: Actual configuration installation\n4. **Profile System**: Profile switching and management\n5. **MCP Server Management**: Modular MCP server installation\n\nWould you like to continue with implementing the configuration management core, or would you prefer to focus on a specific aspect like the installation system or profile management? The CLI framework is ready to support whatever direction you'd like to take next!"
        }
      }
    ]
  ],
  "valid_history_range": [
    0,
    35
  ],
  "transcript": [
    "> In the current folder you will find the configuration files for Amazon Q CLI, I want to build a robust way to load the contexts, profiles and hooks into Amazon Q CLI, so I can share that with others. What would be your recommendation?",
    "Let me first examine the current folder structure to understand your Amazon Q CLI configuration setup.\n[Tool uses: fs_read]",
    "Now let me examine the key configuration files to understand the structure:\n[Tool uses: fs_read]",
    "\n[Tool uses: fs_read]",
    "\n[Tool uses: fs_read]",
    "Let me examine the profiles and hooks structure:\n[Tool uses: fs_read]",
    "\n[Tool uses: fs_read]",
    "\n[Tool uses: fs_read]",
    "\n[Tool uses: fs_read]",
    "\n[Tool uses: fs_read]",
    "\n[Tool uses: fs_read]",
    "Based on my analysis of your Amazon Q CLI configuration, here's my recommendation for building a robust, shareable configuration system:\n\n## Recommended Approach: Configuration as Code with Setup Scripts\n\n### 1. Create a Structured Repository Layout\n\n```\namazonq-config/\n├── README.md\n├── setup.sh                    # Main setup script\n├── config/\n│   ├── mcp.json               # MCP server configurations\n│   ├── global_context.json   # Global context paths\n│   └── profiles/              # Profile configurations\n│       ├── default/\n│       ├── development/\n│       └── production/\n├── contexts/                  # Shared context files\n│   ├── common.md\n│   ├── aws-best-practices.md\n│   └── project-specific/\n├── hooks/                     # Hook scripts and configs\n│   ├── config.yaml\n│   ├── ai_hooks.py\n│   └── ai_hooks.sh\n└── scripts/\n    ├── install-dependencies.sh\n    ├── validate-config.sh\n    └── backup-existing.sh\n```\n\n### 2. Create a Smart Setup Script\n[Tool uses: fs_write]",
    "> wait, let's do planning first, before implementation. I'm thinking more like some context, profiles and hooks repo with an installer, what do you think?",
    "You're absolutely right - let's think through the planning first. Based on your current setup, I can see you have a sophisticated configuration with MCP servers, profiles, hooks, and contexts. Here's my strategic recommendation:\n\n## Planning: Amazon Q CLI Configuration Distribution System\n\n### **Core Concept: Modular Configuration Repository**\n\nCreate a repository structure that separates concerns and allows for easy customization:\n\n```\namazonq-shared-config/\n├── README.md\n├── install.sh                 # One-command installer\n├── configs/\n│   ├── mcp-servers/           # Modular MCP server definitions\n│   │   ├── core.json         # Essential servers (fetch, aws-core)\n│   │   ├── development.json  # Dev tools (outlook, internal tools)\n│   │   └── specialized.json  # Domain-specific (cloudhsm, diagrams)\n│   └── profiles/             # Pre-built profiles\n│       ├── aws-developer/\n│       ├── solutions-architect/\n│       └── enterprise-admin/\n├── contexts/                  # Shared knowledge base\n│   ├── aws-best-practices.md\n│   ├── security-guidelines.md\n│   └── troubleshooting.md\n├── hooks/                     # Automation scripts\n│   ├── context-loader.py\n│   └── profile-switcher.sh\n└── templates/                 # Customizable templates\n    ├── mcp-template.json\n    └── profile-template.json\n```\n\n### **Key Design Principles:**\n\n1. **Modularity**: Users can pick and choose components\n2. **Layered Configuration**: Base → Role-specific → Personal customizations\n3. **Version Control Friendly**: All configs in plain text/JSON\n4. **Environment Agnostic**: Works across different setups\n5. **Backward Compatible**: Preserves existing configurations\n\n### **Installation Strategy:**\n\n```bash\n# Simple one-liner installation\ncurl -sSL https://raw.githubusercontent.com/your-org/amazonq-config/main/install.sh | bash\n\n# Or with customization\n./install.sh --profile=solutions-architect --mcp=core,development\n```\n\n### **Configuration Layers:**\n\n1. **Base Layer**: Essential MCP servers (fetch, aws-core)\n2. **Role Layer**: Job-function specific configs (developer, SA, admin)\n3. **Personal Layer**: Individual customizations (preserved during updates)\n\n### **Smart Features:**\n\n- **Conflict Resolution**: Merge strategies for existing configs\n- **Selective Updates**: Update only specific components\n- **Profile Switching**: Easy switching between different work contexts\n- **Validation**: Pre-flight checks for dependencies and compatibility\n\n### **Questions for You:**\n\n1. **Target Audience**: Who will be using this? (Internal team, open source, enterprise?)\n2. **Update Strategy**: How often do you expect configurations to change?\n3. **Customization Level**: How much personalization should be preserved vs. standardized?\n4. **Dependencies**: Should the installer handle MCP server installations too?\n5. **Backup Strategy**: How aggressive should we be about preserving existing configs?\n\nWhat aspects of this approach resonate with your vision? Any specific requirements or constraints I should consider?\n[Tool uses: none]",
    "> the thing is, it should run on linux, windows, macos... would it be better to build an application that does this?",
    "Great point! Cross-platform compatibility changes the game significantly. Let me think through the options:\n\n## Cross-Platform Approach Analysis\n\n### **Option 1: Shell Script + Platform Detection**\n```bash\n# Works but gets messy fast\nif [[ \"$OSTYPE\" == \"darwin\"* ]]; then\n    # macOS\nelif [[ \"$OSTYPE\" == \"linux-gnu\"* ]]; then\n    # Linux\nelif [[ \"$OSTYPE\" == \"msys\" ]] || [[ \"$OSTYPE\" == \"cygwin\" ]]; then\n    # Windows\nfi\n```\n**Pros**: Simple, no dependencies\n**Cons**: Windows compatibility nightmare, limited error handling\n\n### **Option 2: Python Application** ⭐ **RECOMMENDED**\n```python\n# Cross-platform by design\nimport platform\nimport shutil\nfrom pathlib import Path\n```\n**Pros**: \n- Native cross-platform support\n- Rich ecosystem (click, pydantic, rich for UI)\n- Easy JSON/YAML handling\n- Better error handling and validation\n- Can be packaged as standalone executable\n\n### **Option 3: Go Application**\n**Pros**: Single binary, fast, no runtime dependencies\n**Cons**: More complex for JSON manipulation, overkill for config management\n\n### **Option 4: Node.js Application**\n**Pros**: Great JSON handling, cross-platform\n**Cons**: Runtime dependency, larger footprint\n\n## **My Recommendation: Python CLI Application**\n\nHere's why Python makes the most sense:\n\n### **Architecture:**\n```\namazonq-config-manager/\n├── amazonq_config/\n│   ├── __init__.py\n│   ├── cli.py              # Click-based CLI\n│   ├── installer.py        # Core installation logic\n│   ├── config_manager.py   # Config file operations\n│   ├── platform_utils.py   # OS-specific paths/operations\n│   └── validators.py       # Configuration validation\n├── configs/                # Same as before\n├── contexts/              # Same as before\n├── hooks/                 # Same as before\n├── setup.py\n├── requirements.txt\n└── README.md\n```\n\n### **Installation Options:**\n```bash\n# Via pip (easiest)\npip install amazonq-config-manager\n\n# Via pipx (isolated)\npipx install amazonq-config-manager\n\n# Standalone executable (no Python needed)\n# Built with PyInstaller for each platform\n```\n\n### **Usage:**\n```bash\n# Install base configuration\namazonq-config install\n\n# Install with specific profile\namazonq-config install --profile solutions-architect\n\n# Update existing configuration\namazonq-config update --preserve-personal\n\n# Switch profiles\namazonq-config profile switch development\n\n# Validate current setup\namazonq-config validate\n\n# Backup current config\namazonq-config backup\n```\n\n### **Cross-Platform Benefits:**\n- **Path Handling**: `pathlib.Path` handles Windows/Unix paths automatically\n- **File Operations**: Python's `shutil` works everywhere\n- **JSON/YAML**: Native support with proper error handling\n- **User Input**: Rich prompts and confirmations\n- **Logging**: Proper logging with different levels\n- **Packaging**: Can create standalone executables for each platform\n\n### **Key Features:**\n1. **Smart Merging**: Intelligently merge existing configs\n2. **Rollback**: Easy rollback if something goes wrong\n3. **Validation**: Pre-flight checks for all dependencies\n4. **Interactive Mode**: Guided setup for new users\n5. **CI/CD Friendly**: Silent mode for automated deployments\n\nWould you like me to start with a basic Python CLI structure, or do you prefer a different approach? The Python route gives us the most flexibility and maintainability for cross-platform config management.\n[Tool uses: none]",
    "> I think that's a good idea, let's do a python implementation. Let's move to a new folder and implement this freshly, let's use ~/dev/ai-configurator/ as folder... shall I `cd` into this for the remaining session? I think it would be good to create a task list there",
    "Absolutely! Let's start fresh with a Python implementation. Yes, please `cd` into that directory - it'll make our work much cleaner.\n[Tool uses: execute_bash]",
    "> t",
    "Now let's create a comprehensive task list and project structure:\n[Tool uses: fs_write]",
    "> t",
    "Now let's create the initial project structure:\n[Tool uses: fs_write]",
    "\n[Tool uses: execute_bash]",
    "\n[Tool uses: fs_write]",
    "Now let's create the basic CLI structure:\n[Tool uses: fs_write]",
    "\n[Tool uses: fs_write]",
    "Now let's create the core platform management module:\n[Tool uses: fs_write]",
    "\n[Tool uses: fs_write]",
    "Let's create the core module init files:\n[Tool uses: fs_write]",
    "\n[Tool uses: fs_write]",
    "\n[Tool uses: fs_write]",
    "Now let's create a virtual environment and test our basic CLI:\n[Tool uses: execute_bash]",
    "\n[Tool uses: execute_bash]",
    "Let me fix the pyproject.toml file - there's an issue with the classifier:\n[Tool uses: fs_write]",
    "Now let's try installing again:\n[Tool uses: execute_bash]",
    "Great! Now let's test our CLI:\n[Tool uses: execute_bash]",
    "\n[Tool uses: execute_bash]",
    "\n[Tool uses: execute_bash]",
    "Perfect! Our basic CLI is working. Let's update our task list to reflect our progress:\n[Tool uses: fs_write]",
    "\n[Tool uses: fs_write]",
    "Excellent! We've made great progress. Here's what we've accomplished:\n\n## ✅ **What We've Built So Far:**\n\n1. **Complete Project Structure**: Organized Python package with proper module hierarchy\n2. **Cross-Platform CLI**: Working command-line interface using Click framework\n3. **Platform Detection**: Smart detection of Windows/macOS/Linux with appropriate path handling\n4. **Rich UI**: Beautiful terminal output with colors and panels\n5. **Logging System**: Configurable logging with Rich integration\n6. **Package Management**: Proper pyproject.toml with dependencies and development tools\n\n## 🎯 **Current Status:**\n- **Phase 1**: 60% complete\n- **Working CLI**: `ai-config` command is functional\n- **Platform Support**: Detects Amazon Q CLI installation and config paths\n- **Foundation**: Solid base for building advanced features\n\n## 🚀 **Next Steps:**\nThe foundation is solid! Now we can focus on the core functionality:\n\n1. **Configuration Management**: JSON/YAML parsing and validation\n2. **Backup System**: Safe backup and restore operations\n3. **Installation Logic**: Actual configuration installation\n4. **Profile System**: Profile switching and management\n5. **MCP Server Management**: Modular MCP server installation\n\nWould you like to continue with implementing the configuration management core, or would you prefer to focus on a specific aspect like the installation system or profile management? The CLI framework is ready to support whatever direction you'd like to take next!\n[Tool uses: none]",
    "> !cd ~/dev/ai-configurator",
    "> !pwd",
    "> /save ~/dev/ai-configurator/q_conversation.md",
    "> /save /Users/janossch/dev/ai-configurator/q_conversation.md"
  ],
  "tools": {
    "awslabsaws_documentation_mcp_server": [
      {
        "ToolSpecification": {
          "name": "awslabsaws_documentation_mcp_server___read_documentation",
          "description": "Fetch and convert an AWS documentation page to markdown format.\n\n    ## Usage\n\n    This tool retrieves the content of an AWS documentation page and converts it to markdown format.\n    For long documents, you can make multiple calls with different start_index values to retrieve\n    the entire content in chunks.\n\n    ## URL Requirements\n\n    - Must be from the docs.aws.amazon.com domain\n    - Must end with .html\n\n    ## Example URLs\n\n    - https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucketnamingrules.html\n    - https://docs.aws.amazon.com/lambda/latest/dg/lambda-invocation.html\n\n    ## Output Format\n\n    The output is formatted as markdown text with:\n    - Preserved headings and structure\n    - Code blocks for examples\n    - Lists and tables converted to markdown format\n\n    ## Handling Long Documents\n\n    If the response indicates the document was truncated, you have several options:\n\n    1. **Continue Reading**: Make another call with start_index set to the end of the previous response\n    2. **Stop Early**: For very long documents (>30,000 characters), if you've already found the specific information needed, you can stop reading\n\n    Args:\n        ctx: MCP context for logging and error handling\n        url: URL of the AWS documentation page to read\n        max_length: Maximum number of characters to return\n        start_index: On return output starting at this character index\n\n    Returns:\n        Markdown content of the AWS documentation\n    ",
          "input_schema": {
            "json": {
              "type": "object",
              "required": [
                "url"
              ],
              "properties": {
                "start_index": {
                  "title": "Start Index",
                  "default": 0,
                  "description": "On return output starting at this character index, useful if a previous fetch was truncated and more content is required.",
                  "minimum": 0,
                  "type": "integer"
                },
                "max_length": {
                  "title": "Max Length",
                  "type": "integer",
                  "default": 5000,
                  "exclusiveMaximum": 1000000,
                  "exclusiveMinimum": 0,
                  "description": "Maximum number of characters to return."
                },
                "url": {
                  "description": "URL of the AWS documentation page to read",
                  "title": "Url",
                  "type": "string"
                }
              },
              "title": "read_documentationArguments"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "awslabsaws_documentation_mcp_server___search_documentation",
          "description": "Search AWS documentation using the official AWS Documentation Search API.\n\n    ## Usage\n\n    This tool searches across all AWS documentation for pages matching your search phrase.\n    Use it to find relevant documentation when you don't have a specific URL.\n\n    ## Search Tips\n\n    - Use specific technical terms rather than general phrases\n    - Include service names to narrow results (e.g., \"S3 bucket versioning\" instead of just \"versioning\")\n    - Use quotes for exact phrase matching (e.g., \"AWS Lambda function URLs\")\n    - Include abbreviations and alternative terms to improve results\n\n    ## Result Interpretation\n\n    Each result includes:\n    - rank_order: The relevance ranking (lower is more relevant)\n    - url: The documentation page URL\n    - title: The page title\n    - context: A brief excerpt or summary (if available)\n\n    Args:\n        ctx: MCP context for logging and error handling\n        search_phrase: Search phrase to use\n        limit: Maximum number of results to return\n\n    Returns:\n        List of search results with URLs, titles, and context snippets\n    ",
          "input_schema": {
            "json": {
              "title": "search_documentationArguments",
              "properties": {
                "search_phrase": {
                  "description": "Search phrase to use",
                  "title": "Search Phrase",
                  "type": "string"
                },
                "limit": {
                  "title": "Limit",
                  "default": 10,
                  "description": "Maximum number of results to return",
                  "maximum": 50,
                  "minimum": 1,
                  "type": "integer"
                }
              },
              "required": [
                "search_phrase"
              ],
              "type": "object"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "awslabsaws_documentation_mcp_server___recommend",
          "description": "Get content recommendations for an AWS documentation page.\n\n    ## Usage\n\n    This tool provides recommendations for related AWS documentation pages based on a given URL.\n    Use it to discover additional relevant content that might not appear in search results.\n\n    ## Recommendation Types\n\n    The recommendations include four categories:\n\n    1. **Highly Rated**: Popular pages within the same AWS service\n    2. **New**: Recently added pages within the same AWS service - useful for finding newly released features\n    3. **Similar**: Pages covering similar topics to the current page\n    4. **Journey**: Pages commonly viewed next by other users\n\n    ## When to Use\n\n    - After reading a documentation page to find related content\n    - When exploring a new AWS service to discover important pages\n    - To find alternative explanations of complex concepts\n    - To discover the most popular pages for a service\n    - To find newly released information by using a service's welcome page URL and checking the **New** recommendations\n\n    ## Finding New Features\n\n    To find newly released information about a service:\n    1. Find any page belong to that service, typically you can try the welcome page\n    2. Call this tool with that URL\n    3. Look specifically at the **New** recommendation type in the results\n\n    ## Result Interpretation\n\n    Each recommendation includes:\n    - url: The documentation page URL\n    - title: The page title\n    - context: A brief description (if available)\n\n    Args:\n        ctx: MCP context for logging and error handling\n        url: URL of the AWS documentation page to get recommendations for\n\n    Returns:\n        List of recommended pages with URLs, titles, and context\n    ",
          "input_schema": {
            "json": {
              "required": [
                "url"
              ],
              "title": "recommendArguments",
              "type": "object",
              "properties": {
                "url": {
                  "title": "Url",
                  "description": "URL of the AWS documentation page to get recommendations for",
                  "type": "string"
                }
              }
            }
          }
        }
      }
    ],
    "outlook_mcp_server": [
      {
        "ToolSpecification": {
          "name": "outlook_mcp_server___outlook_database_query",
          "description": "\n        Execute a custom read-only SQL query against the Outlook database.\n        \n        TOOL HIERARCHY - IMPORTANT:\n        This tool should be used as a LAST RESORT after trying more specialized tools:\n        1. mailbox_overview - For getting comprehensive mailbox statistics including categories\n        2. unified_email_search - For searching emails with advanced filtering\n        3. email_volume_analytics - For analyzing email volume over time\n        4. sender_statistics - For analyzing sender patterns\n        5. folder_analytics - For analyzing folder usage\n        \n        IMPORTANT: This tool should be used in a two-step process:\n        \n        STEP 1: ALWAYS call this tool first with an empty query (query=\"\") to retrieve the complete \n        database schema, table structure, and example queries. Example:\n            outlook_database_query(query=\"\")\n        \n        STEP 2: After reviewing the schema, call this tool again with your specific SQL query.\n        \n        This tool allows direct read-only SQL queries against the Outlook database structure for advanced\n        or unique information retrieval needs when existing specialized tools cannot fulfill the request.\n        \n        Args:\n            query: SQL query to execute (must be SELECT only) or empty string to get schema\n            params: Optional parameters for the query\n            max_results: Maximum number of results to return\n            \n        Returns:\n            Dictionary with query results and metadata or complete schema information\n        ",
          "input_schema": {
            "json": {
              "required": [
                "query"
              ],
              "properties": {
                "params": {
                  "title": "Params",
                  "default": null,
                  "anyOf": [
                    {
                      "type": "object"
                    },
                    {
                      "type": "null"
                    }
                  ]
                },
                "query": {
                  "title": "Query",
                  "type": "string"
                },
                "max_results": {
                  "title": "Max Results",
                  "default": 1000,
                  "type": "integer"
                }
              },
              "title": "outlook_database_queryArguments",
              "type": "object"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "outlook_mcp_server___unified_email_search",
          "description": "\n        Unified search tool for finding emails with advanced filtering.\n        \n        Args:\n            query: Text to search in subject or preview\n            folders: List of folder names to search in\n            account: Email address of account to search in\n            is_unread: Filter by read/unread status\n            has_attachment: Filter by attachment presence\n            is_flagged: Filter by flag status (True for flagged emails)\n            category: Filter by category name\n            date_filter: Date filter string (e.g., 'today', 'this week', 'last 30 days', '2025-06-01..2025-06-30')\n            sender: Filter by sender\n            subject: Filter by subject\n            limit: Maximum number of results to return\n            offset: Offset for pagination\n            \n        Returns:\n            Dictionary with search results and metadata\n        ",
          "input_schema": {
            "json": {
              "title": "unified_email_searchArguments",
              "properties": {
                "offset": {
                  "type": "integer",
                  "default": 0,
                  "title": "Offset"
                },
                "query": {
                  "anyOf": [
                    {
                      "type": "string"
                    },
                    {
                      "type": "null"
                    }
                  ],
                  "default": null,
                  "title": "Query"
                },
                "account": {
                  "anyOf": [
                    {
                      "type": "string"
                    },
                    {
                      "type": "null"
                    }
                  ],
                  "default": null,
                  "title": "Account"
                },
                "sender": {
                  "default": null,
                  "title": "Sender",
                  "anyOf": [
                    {
                      "type": "string"
                    },
                    {
                      "type": "null"
                    }
                  ]
                },
                "folders": {
                  "default": null,
                  "anyOf": [
                    {
                      "type": "array",
                      "items": {
                        "type": "string"
                      }
                    },
                    {
                      "type": "null"
                    }
                  ],
                  "title": "Folders"
                },
                "category": {
                  "default": null,
                  "title": "Category",
                  "anyOf": [
                    {
                      "type": "string"
                    },
                    {
                      "type": "null"
                    }
                  ]
                },
                "subject": {
                  "anyOf": [
                    {
                      "type": "string"
                    },
                    {
                      "type": "null"
                    }
                  ],
                  "default": null,
                  "title": "Subject"
                },
                "has_attachment": {
                  "anyOf": [
                    {
                      "type": "boolean"
                    },
                    {
                      "type": "null"
                    }
                  ],
                  "default": null,
                  "title": "Has Attachment"
                },
                "is_flagged": {
                  "title": "Is Flagged",
                  "anyOf": [
                    {
                      "type": "boolean"
                    },
                    {
                      "type": "null"
                    }
                  ],
                  "default": null
                },
                "is_unread": {
                  "title": "Is Unread",
                  "default": null,
                  "anyOf": [
                    {
                      "type": "boolean"
                    },
                    {
                      "type": "null"
                    }
                  ]
                },
                "date_filter": {
                  "anyOf": [
                    {
                      "type": "string"
                    },
                    {
                      "type": "null"
                    }
                  ],
                  "title": "Date Filter",
                  "default": null
                },
                "limit": {
                  "default": 100,
                  "type": "integer",
                  "title": "Limit"
                }
              },
              "type": "object"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "outlook_mcp_server___search_calendar_events",
          "description": "Search for calendar events across all calendars\n    \n    Args:\n        query: Search query string to match against event subject, location, or content.\n              Special formats supported:\n              - \"today\" - Find events scheduled for today\n              - \"YYYY-MM-DD\" (e.g., \"2025-04-24\") - Find events on specific date\n              - \"Month Day\" or \"Month Day, Year\" (e.g., \"April 24\" or \"April 24, 2025\")\n        max_results: Maximum number of results to return (default: 100)\n        \n    Returns:\n        List of calendar events matching the search query\n    ",
          "input_schema": {
            "json": {
              "properties": {
                "max_results": {
                  "type": "integer",
                  "default": 100,
                  "title": "Max Results"
                },
                "query": {
                  "type": "string",
                  "title": "Query"
                }
              },
              "title": "search_calendar_eventsArguments",
              "required": [
                "query"
              ],
              "type": "object"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "outlook_mcp_server___delete_email",
          "description": "Delete an email or multiple emails from Outlook\n    \n    Args:\n        message_id: ID of the message to delete or a list of message IDs to delete multiple emails\n        email: Optional source email address to use (your local Outlook account)\n        account_type: Optional account type ('Exchange', 'POP3', 'IMAP')\n    \n    Returns:\n        Dictionary with status of the operation\n    ",
          "input_schema": {
            "json": {
              "required": [
                "message_id"
              ],
              "properties": {
                "message_id": {
                  "anyOf": [
                    {
                      "type": "string"
                    },
                    {
                      "items": {
                        "type": "string"
                      },
                      "type": "array"
                    }
                  ],
                  "title": "Message Id"
                },
                "email": {
                  "title": "Email",
                  "default": null,
                  "anyOf": [
                    {
                      "type": "string"
                    },
                    {
                      "type": "null"
                    }
                  ]
                },
                "account_type": {
                  "title": "Account Type",
                  "anyOf": [
                    {
                      "type": "string"
                    },
                    {
                      "type": "null"
                    }
                  ],
                  "default": null
                }
              },
              "title": "delete_emailArguments",
              "type": "object"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "outlook_mcp_server___folder_analytics",
          "description": "\n        Get statistics about email folders.\n        \n        Args:\n            account: Email address of account to analyze\n            include_empty: Whether to include empty folders\n            \n        Returns:\n            Dictionary with folder statistics\n        ",
          "input_schema": {
            "json": {
              "title": "folder_analyticsArguments",
              "type": "object",
              "properties": {
                "include_empty": {
                  "title": "Include Empty",
                  "type": "boolean",
                  "default": false
                },
                "account": {
                  "anyOf": [
                    {
                      "type": "string"
                    },
                    {
                      "type": "null"
                    }
                  ],
                  "default": null,
                  "title": "Account"
                }
              }
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "outlook_mcp_server___get_calendar_events",
          "description": "Get events from a specific calendar with optional date range\n    \n    Args:\n        calendar_id: ID of the calendar to get events from\n        start_date: Optional start date in format 'YYYY-MM-DD'\n        end_date: Optional end date in format 'YYYY-MM-DD' (must be greater than start_date)\n        \n    Returns:\n        List of calendar events from the specified calendar\n    ",
          "input_schema": {
            "json": {
              "properties": {
                "calendar_id": {
                  "title": "Calendar Id",
                  "type": "integer"
                },
                "start_date": {
                  "anyOf": [
                    {
                      "type": "string"
                    },
                    {
                      "type": "null"
                    }
                  ],
                  "title": "Start Date",
                  "default": null
                },
                "end_date": {
                  "anyOf": [
                    {
                      "type": "string"
                    },
                    {
                      "type": "null"
                    }
                  ],
                  "title": "End Date",
                  "default": null
                }
              },
              "title": "get_calendar_eventsArguments",
              "required": [
                "calendar_id"
              ],
              "type": "object"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "outlook_mcp_server___sender_analytics",
          "description": "\n        Get statistics about email senders.\n        \n        Args:\n            account: Email address of account to analyze\n            date_filter: Date filter string (e.g., 'last 30 days')\n            limit: Maximum number of senders to return\n            \n        Returns:\n            Dictionary with sender statistics\n        ",
          "input_schema": {
            "json": {
              "title": "sender_analyticsArguments",
              "properties": {
                "date_filter": {
                  "anyOf": [
                    {
                      "type": "string"
                    },
                    {
                      "type": "null"
                    }
                  ],
                  "default": null,
                  "title": "Date Filter"
                },
                "limit": {
                  "title": "Limit",
                  "default": 20,
                  "type": "integer"
                },
                "account": {
                  "anyOf": [
                    {
                      "type": "string"
                    },
                    {
                      "type": "null"
                    }
                  ],
                  "default": null,
                  "title": "Account"
                }
              },
              "type": "object"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "outlook_mcp_server___reply_to_email_as_html",
          "description": "Reply to an email with HTML content in Outlook\n    \n    Args:\n        message_id: ID of the message to reply to\n        reply_text: HTML-formatted content for the reply\n        email: Optional source email address to use (your local Outlook account)\n        account_type: Optional account type ('Exchange', 'POP3', 'IMAP')\n    \n    Returns:\n        Dictionary with status of the operation\n    ",
          "input_schema": {
            "json": {
              "title": "reply_to_email_as_htmlArguments",
              "type": "object",
              "properties": {
                "message_id": {
                  "type": "string",
                  "title": "Message Id"
                },
                "reply_text": {
                  "title": "Reply Text",
                  "type": "string"
                },
                "account_type": {
                  "anyOf": [
                    {
                      "type": "string"
                    },
                    {
                      "type": "null"
                    }
                  ],
                  "default": null,
                  "title": "Account Type"
                },
                "email": {
                  "title": "Email",
                  "default": null,
                  "anyOf": [
                    {
                      "type": "string"
                    },
                    {
                      "type": "null"
                    }
                  ]
                }
              },
              "required": [
                "message_id",
                "reply_text"
              ]
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "outlook_mcp_server___save_attachments",
          "description": "Save attachments from a specific email to a local directory\n    \n    Args:\n        message_id: ID of the message containing attachments\n        save_path: Local directory path where attachments should be saved\n        email: Optional source email address to use (your local Outlook account)\n        account_type: Optional account type ('Exchange', 'POP3', 'IMAP')\n    \n    Returns:\n        List of dictionaries containing information about saved attachments:\n        - name: Filename of the attachment\n        - size: Size of the file in bytes\n        - type: MIME type of the attachment\n        - path: Full path where the file was saved\n    ",
          "input_schema": {
            "json": {
              "title": "save_attachmentsArguments",
              "required": [
                "message_id",
                "save_path"
              ],
              "properties": {
                "save_path": {
                  "title": "Save Path",
                  "type": "string"
                },
                "email": {
                  "default": null,
                  "anyOf": [
                    {
                      "type": "string"
                    },
                    {
                      "type": "null"
                    }
                  ],
                  "title": "Email"
                },
                "account_type": {
                  "anyOf": [
                    {
                      "type": "string"
                    },
                    {
                      "type": "null"
                    }
                  ],
                  "title": "Account Type",
                  "default": null
                },
                "message_id": {
                  "title": "Message Id",
                  "type": "string"
                }
              },
              "type": "object"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "outlook_mcp_server___get_calendars",
          "description": "Get a list of available calendars in Outlook\n    \n    Args:\n        email: Optional source email address to use (your local Outlook account)\n        account_type: Optional account type ('Exchange', 'POP3', 'IMAP')\n    \n    Returns:\n        List of calendar information including name and ID\n    ",
          "input_schema": {
            "json": {
              "title": "get_calendarsArguments",
              "properties": {
                "email": {
                  "anyOf": [
                    {
                      "type": "string"
                    },
                    {
                      "type": "null"
                    }
                  ],
                  "title": "Email",
                  "default": null
                },
                "account_type": {
                  "title": "Account Type",
                  "anyOf": [
                    {
                      "type": "string"
                    },
                    {
                      "type": "null"
                    }
                  ],
                  "default": null
                }
              },
              "type": "object"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "outlook_mcp_server___clear_category",
          "description": "Clear a specific category or all categories from an email or multiple emails in Outlook\n    \n    Args:\n        message_id: ID of the message to clear categories from or a list of message IDs\n        category_name: Name of the category to remove (if empty, all categories will be cleared)\n        email: Optional source email address to use (your local Outlook account)\n        account_type: Optional account type ('Exchange', 'POP3', 'IMAP')\n    \n    Returns:\n        Dictionary with status of the operation\n    ",
          "input_schema": {
            "json": {
              "properties": {
                "category_name": {
                  "default": "",
                  "title": "Category Name",
                  "type": "string"
                },
                "account_type": {
                  "default": null,
                  "anyOf": [
                    {
                      "type": "string"
                    },
                    {
                      "type": "null"
                    }
                  ],
                  "title": "Account Type"
                },
                "message_id": {
                  "anyOf": [
                    {
                      "type": "string"
                    },
                    {
                      "type": "array",
                      "items": {
                        "type": "string"
                      }
                    }
                  ],
                  "title": "Message Id"
                },
                "email": {
                  "default": null,
                  "anyOf": [
                    {
                      "type": "string"
                    },
                    {
                      "type": "null"
                    }
                  ],
                  "title": "Email"
                }
              },
              "required": [
                "message_id"
              ],
              "type": "object",
              "title": "clear_categoryArguments"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "outlook_mcp_server___assign_category",
          "description": "Assign a category to an email or multiple emails in Outlook\n    \n    Args:\n        message_id: ID of the message to categorize or a list of message IDs to categorize multiple emails\n        category_name: Name of the category to assign (will be created if it doesn't exist)\n        email: Optional source email address to use (your local Outlook account)\n        account_type: Optional account type ('Exchange', 'POP3', 'IMAP')\n    \n    Returns:\n        Dictionary with status of the operation\n    ",
          "input_schema": {
            "json": {
              "properties": {
                "message_id": {
                  "title": "Message Id",
                  "anyOf": [
                    {
                      "type": "string"
                    },
                    {
                      "type": "array",
                      "items": {
                        "type": "string"
                      }
                    }
                  ]
                },
                "account_type": {
                  "title": "Account Type",
                  "anyOf": [
                    {
                      "type": "string"
                    },
                    {
                      "type": "null"
                    }
                  ],
                  "default": null
                },
                "category_name": {
                  "title": "Category Name",
                  "type": "string"
                },
                "email": {
                  "title": "Email",
                  "anyOf": [
                    {
                      "type": "string"
                    },
                    {
                      "type": "null"
                    }
                  ],
                  "default": null
                }
              },
              "type": "object",
              "title": "assign_categoryArguments",
              "required": [
                "message_id",
                "category_name"
              ]
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "outlook_mcp_server___email_volume_analytics",
          "description": "\n        Get email volume statistics grouped by time period.\n        \n        Args:\n            account: Email address of account to analyze\n            date_filter: Date filter string (e.g., 'last 30 days')\n            group_by: Time grouping ('day', 'week', 'month')\n            \n        Returns:\n            Dictionary with email volume statistics\n        ",
          "input_schema": {
            "json": {
              "properties": {
                "account": {
                  "title": "Account",
                  "default": null,
                  "anyOf": [
                    {
                      "type": "string"
                    },
                    {
                      "type": "null"
                    }
                  ]
                },
                "date_filter": {
                  "default": null,
                  "title": "Date Filter",
                  "anyOf": [
                    {
                      "type": "string"
                    },
                    {
                      "type": "null"
                    }
                  ]
                },
                "group_by": {
                  "title": "Group By",
                  "type": "string",
                  "default": "day"
                }
              },
              "type": "object",
              "title": "email_volume_analyticsArguments"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "outlook_mcp_server___forward_email_as_html",
          "description": "Forward an email to another recipient with HTML content in the additional text\n    \n    Args:\n        message_id: ID of the message to forward\n        to: Destination recipient email address to forward the email to\n        additional_text: Optional HTML content to add to the beginning of the forwarded message\n        email: Optional source email address to use (your local Outlook account)\n        account_type: Optional account type ('Exchange', 'POP3', 'IMAP')\n    \n    Returns:\n        Dictionary with status of the operation\n    ",
          "input_schema": {
            "json": {
              "properties": {
                "message_id": {
                  "type": "string",
                  "title": "Message Id"
                },
                "account_type": {
                  "default": null,
                  "title": "Account Type",
                  "anyOf": [
                    {
                      "type": "string"
                    },
                    {
                      "type": "null"
                    }
                  ]
                },
                "additional_text": {
                  "title": "Additional Text",
                  "type": "string",
                  "default": ""
                },
                "email": {
                  "anyOf": [
                    {
                      "type": "string"
                    },
                    {
                      "type": "null"
                    }
                  ],
                  "title": "Email",
                  "default": null
                },
                "to": {
                  "title": "To",
                  "type": "string"
                }
              },
              "required": [
                "message_id",
                "to"
              ],
              "title": "forward_email_as_htmlArguments",
              "type": "object"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "outlook_mcp_server___create_draft_as_html",
          "description": "Create a draft email with HTML content in Outlook\n    \n    Args:\n        to: Destination recipient email address for the draft\n        subject: Email subject\n        body: HTML-formatted content for the email body\n        email: Optional source email address to use (your local Outlook account)\n        account_type: Optional account type ('Exchange', 'POP3', 'IMAP')\n    \n    Returns:\n        Dictionary with status of the operation\n    ",
          "input_schema": {
            "json": {
              "type": "object",
              "properties": {
                "email": {
                  "anyOf": [
                    {
                      "type": "string"
                    },
                    {
                      "type": "null"
                    }
                  ],
                  "title": "Email",
                  "default": null
                },
                "subject": {
                  "title": "Subject",
                  "type": "string"
                },
                "to": {
                  "type": "string",
                  "title": "To"
                },
                "body": {
                  "title": "Body",
                  "type": "string"
                },
                "account_type": {
                  "anyOf": [
                    {
                      "type": "string"
                    },
                    {
                      "type": "null"
                    }
                  ],
                  "title": "Account Type",
                  "default": null
                }
              },
              "required": [
                "to",
                "subject",
                "body"
              ],
              "title": "create_draft_as_htmlArguments"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "outlook_mcp_server___mark_as_unread",
          "description": "Mark an email as unread in Outlook\n    \n    Args:\n        message_id: ID of the message to mark as unread\n        email: Optional source email address to use (your local Outlook account)\n        account_type: Optional account type ('Exchange', 'POP3', 'IMAP')\n    \n    Returns:\n        Dictionary with status of the operation\n    ",
          "input_schema": {
            "json": {
              "properties": {
                "message_id": {
                  "anyOf": [
                    {
                      "type": "string"
                    },
                    {
                      "items": {
                        "type": "string"
                      },
                      "type": "array"
                    }
                  ],
                  "title": "Message Id"
                },
                "email": {
                  "anyOf": [
                    {
                      "type": "string"
                    },
                    {
                      "type": "null"
                    }
                  ],
                  "default": null,
                  "title": "Email"
                },
                "account_type": {
                  "anyOf": [
                    {
                      "type": "string"
                    },
                    {
                      "type": "null"
                    }
                  ],
                  "default": null,
                  "title": "Account Type"
                }
              },
              "required": [
                "message_id"
              ],
              "title": "mark_as_unreadArguments",
              "type": "object"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "outlook_mcp_server___mailbox_overview",
          "description": "\n        Get a comprehensive overview of the mailbox.\n        \n        Args:\n            account: Email address of account to analyze\n            \n        Returns:\n            Dictionary with mailbox overview statistics\n        ",
          "input_schema": {
            "json": {
              "title": "mailbox_overviewArguments",
              "type": "object",
              "properties": {
                "account": {
                  "default": null,
                  "anyOf": [
                    {
                      "type": "string"
                    },
                    {
                      "type": "null"
                    }
                  ],
                  "title": "Account"
                }
              }
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "outlook_mcp_server___get_email_content",
          "description": "Get the full content of a specific email\n    \n    Args:\n        message_id: ID of the message to retrieve\n        email: Optional source email address to use (your local Outlook account)\n        account_type: Optional account type ('Exchange', 'POP3', 'IMAP')\n    \n    Returns:\n        Dictionary with email details including subject, sender, date, and content\n    ",
          "input_schema": {
            "json": {
              "required": [
                "message_id"
              ],
              "type": "object",
              "properties": {
                "account_type": {
                  "anyOf": [
                    {
                      "type": "string"
                    },
                    {
                      "type": "null"
                    }
                  ],
                  "default": null,
                  "title": "Account Type"
                },
                "message_id": {
                  "title": "Message Id",
                  "type": "string"
                },
                "email": {
                  "default": null,
                  "anyOf": [
                    {
                      "type": "string"
                    },
                    {
                      "type": "null"
                    }
                  ],
                  "title": "Email"
                }
              },
              "title": "get_email_contentArguments"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "outlook_mcp_server___send_email_as_html",
          "description": "Send an email with HTML content using Outlook\n    \n    Args:\n        to: Destination recipient email address to send the email to\n        subject: Email subject\n        body: HTML-formatted content for the email body\n        email: Optional source email address to use (your local Outlook account)\n        account_type: Optional account type ('Exchange', 'POP3', 'IMAP')\n    \n    Returns:\n        Dictionary with status of the operation\n    ",
          "input_schema": {
            "json": {
              "type": "object",
              "required": [
                "to",
                "subject",
                "body"
              ],
              "title": "send_email_as_htmlArguments",
              "properties": {
                "email": {
                  "anyOf": [
                    {
                      "type": "string"
                    },
                    {
                      "type": "null"
                    }
                  ],
                  "title": "Email",
                  "default": null
                },
                "subject": {
                  "type": "string",
                  "title": "Subject"
                },
                "account_type": {
                  "title": "Account Type",
                  "default": null,
                  "anyOf": [
                    {
                      "type": "string"
                    },
                    {
                      "type": "null"
                    }
                  ]
                },
                "body": {
                  "type": "string",
                  "title": "Body"
                },
                "to": {
                  "type": "string",
                  "title": "To"
                }
              }
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "outlook_mcp_server___list_tools",
          "description": "List all available tools in this MCP server",
          "input_schema": {
            "json": {
              "properties": {},
              "title": "list_toolsArguments",
              "type": "object"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "outlook_mcp_server___debug_search",
          "description": "Debug email search functionality\n    \n    Args:\n        query: Search query to test\n        email: Optional source email address to use (your local Outlook account)\n        account_type: Optional account type ('Exchange', 'POP3', 'IMAP')\n    \n    Returns:\n        Debug information about the search operation\n    ",
          "input_schema": {
            "json": {
              "type": "object",
              "title": "debug_searchArguments",
              "required": [
                "query"
              ],
              "properties": {
                "account_type": {
                  "anyOf": [
                    {
                      "type": "string"
                    },
                    {
                      "type": "null"
                    }
                  ],
                  "title": "Account Type",
                  "default": null
                },
                "query": {
                  "type": "string",
                  "title": "Query"
                },
                "email": {
                  "title": "Email",
                  "default": null,
                  "anyOf": [
                    {
                      "type": "string"
                    },
                    {
                      "type": "null"
                    }
                  ]
                }
              }
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "outlook_mcp_server___get_event_details",
          "description": "Get detailed information about a specific calendar event\n    \n    Args:\n        event_id: ID of the event to get details for\n        \n    Returns:\n        Dictionary with detailed event information including:\n        - Basic event details (subject, time, location)\n        - My response status (accepted, tentative, none)\n        - Free/busy status (free, busy, tentative, out of office)\n        - Organizer and attendees with their response status\n    ",
          "input_schema": {
            "json": {
              "type": "object",
              "properties": {
                "event_id": {
                  "title": "Event Id",
                  "type": "integer"
                }
              },
              "title": "get_event_detailsArguments",
              "required": [
                "event_id"
              ]
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "outlook_mcp_server___ping",
          "description": "Ping a host and return statistics\n    \n    Args:\n        host: The hostname or IP address to ping\n        count: Number of ping packets to send (default: 4)\n    \n    Returns:\n        Dictionary containing ping statistics\n    ",
          "input_schema": {
            "json": {
              "title": "pingArguments",
              "required": [
                "host"
              ],
              "type": "object",
              "properties": {
                "host": {
                  "title": "Host",
                  "type": "string"
                },
                "count": {
                  "default": 4,
                  "type": "integer",
                  "title": "Count"
                }
              }
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "outlook_mcp_server___mark_as_read",
          "description": "Mark an email as read in Outlook\n    \n    Args:\n        message_id: ID of the message to mark as read\n        email: Optional source email address to use (your local Outlook account)\n        account_type: Optional account type ('Exchange', 'POP3', 'IMAP')\n    \n    Returns:\n        Dictionary with status of the operation\n    ",
          "input_schema": {
            "json": {
              "title": "mark_as_readArguments",
              "required": [
                "message_id"
              ],
              "properties": {
                "account_type": {
                  "title": "Account Type",
                  "anyOf": [
                    {
                      "type": "string"
                    },
                    {
                      "type": "null"
                    }
                  ],
                  "default": null
                },
                "message_id": {
                  "anyOf": [
                    {
                      "type": "string"
                    },
                    {
                      "type": "array",
                      "items": {
                        "type": "string"
                      }
                    }
                  ],
                  "title": "Message Id"
                },
                "email": {
                  "title": "Email",
                  "anyOf": [
                    {
                      "type": "string"
                    },
                    {
                      "type": "null"
                    }
                  ],
                  "default": null
                }
              },
              "type": "object"
            }
          }
        }
      }
    ],
    "awslabscore_mcp_server": [
      {
        "ToolSpecification": {
          "name": "awslabscore_mcp_server___prompt_understanding",
          "description": "MCP-CORE Prompt Understanding.\n\n    ALWAYS Use this tool first to understand the user's query and translate it into AWS expert advice.\n    ",
          "input_schema": {
            "json": {
              "properties": {},
              "type": "object",
              "title": "get_prompt_understandingArguments"
            }
          }
        }
      }
    ],
    "native___": [
      {
        "ToolSpecification": {
          "name": "report_issue",
          "description": "Opens the browser to a pre-filled gh (GitHub) issue template to report chat issues, bugs, or feature requests. Pre-filled information includes the conversation transcript, chat context, and chat request IDs from the service.",
          "input_schema": {
            "json": {
              "required": [
                "title"
              ],
              "properties": {
                "steps_to_reproduce": {
                  "description": "Optional: Previous user chat requests or steps that were taken that may have resulted in the issue or error response.",
                  "type": "string"
                },
                "expected_behavior": {
                  "description": "Optional: The expected chat behavior or action that did not happen.",
                  "type": "string"
                },
                "title": {
                  "type": "string",
                  "description": "The title of the GitHub issue."
                },
                "actual_behavior": {
                  "description": "Optional: The actual chat behavior that happened and demonstrates the issue or lack of a feature.",
                  "type": "string"
                }
              },
              "type": "object"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "execute_bash",
          "description": "Execute the specified bash command.",
          "input_schema": {
            "json": {
              "properties": {
                "command": {
                  "type": "string",
                  "description": "Bash command to execute"
                },
                "summary": {
                  "type": "string",
                  "description": "A brief explanation of what the command does"
                }
              },
              "required": [
                "command"
              ],
              "type": "object"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "fs_read",
          "description": "Tool for reading files (for example, `cat -n`),  directories (for example, `ls -la`) and images. If user has supplied paths that appear to be leading to images, you should use this tool right away using Image mode. The behavior of this tool is determined by the `mode` parameter. The available modes are:\n- line: Show lines in a file, given by an optional `start_line` and optional `end_line`.\n- directory: List directory contents. Content is returned in the \"long format\" of ls (that is, `ls -la`).\n- search: Search for a pattern in a file. The pattern is a string. The matching is case insensitive.\n\nExample Usage:\n1. Read all lines from a file: command=\"line\", path=\"/path/to/file.txt\"\n2. Read the last 5 lines from a file: command=\"line\", path=\"/path/to/file.txt\", start_line=-5\n3. List the files in the home directory: command=\"line\", path=\"~\"\n4. Recursively list files in a directory to a max depth of 2: command=\"line\", path=\"/path/to/directory\", depth=2\n5. Search for all instances of \"test\" in a file: command=\"search\", path=\"/path/to/file.txt\", pattern=\"test\"\n",
          "input_schema": {
            "json": {
              "required": [
                "path",
                "mode"
              ],
              "type": "object",
              "properties": {
                "depth": {
                  "type": "integer",
                  "default": 0,
                  "description": "Depth of a recursive directory listing (optional, for Directory mode)"
                },
                "context_lines": {
                  "description": "Number of context lines around search results (optional, for Search mode)",
                  "default": 2,
                  "type": "integer"
                },
                "pattern": {
                  "type": "string",
                  "description": "Pattern to search for (required, for Search mode). Case insensitive. The pattern matching is performed per line."
                },
                "path": {
                  "type": "string",
                  "description": "Path to the file or directory. The path should be absolute, or otherwise start with ~ for the user's home."
                },
                "end_line": {
                  "type": "integer",
                  "default": -1,
                  "description": "Ending line number (optional, for Line mode). A negative index represents a line number starting from the end of the file."
                },
                "image_paths": {
                  "type": "array",
                  "items": {
                    "type": "string"
                  },
                  "description": "List of paths to the images. This is currently supported by the Image mode."
                },
                "start_line": {
                  "default": 1,
                  "type": "integer",
                  "description": "Starting line number (optional, for Line mode). A negative index represents a line number starting from the end of the file."
                },
                "mode": {
                  "enum": [
                    "Line",
                    "Directory",
                    "Search",
                    "Image"
                  ],
                  "description": "The mode to run in: `Line`, `Directory`, `Search`. `Line` and `Search` are only for text files, and `Directory` is only for directories. `Image` is for image files, in this mode `image_paths` is required.",
                  "type": "string"
                }
              }
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "dummy",
          "description": "This is a dummy tool. If you are seeing this that means the tool associated with this tool call is not in the list of available tools. This could be because a wrong tool name was supplied or the list of tools has changed since the conversation has started. Do not show this when user asks you to list tools.",
          "input_schema": {
            "json": {
              "type": "object",
              "required": [],
              "properties": {}
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "fs_write",
          "description": "A tool for creating and editing files\n * The `create` command will override the file at `path` if it already exists as a file, and otherwise create a new file\n * The `append` command will add content to the end of an existing file, automatically adding a newline if the file doesn't end with one. The file must exist.\n Notes for using the `str_replace` command:\n * The `old_str` parameter should match EXACTLY one or more consecutive lines from the original file. Be mindful of whitespaces!\n * If the `old_str` parameter is not unique in the file, the replacement will not be performed. Make sure to include enough context in `old_str` to make it unique\n * The `new_str` parameter should contain the edited lines that should replace the `old_str`.",
          "input_schema": {
            "json": {
              "type": "object",
              "required": [
                "command",
                "path"
              ],
              "properties": {
                "insert_line": {
                  "type": "integer",
                  "description": "Required parameter of `insert` command. The `new_str` will be inserted AFTER the line `insert_line` of `path`."
                },
                "old_str": {
                  "type": "string",
                  "description": "Required parameter of `str_replace` command containing the string in `path` to replace."
                },
                "summary": {
                  "type": "string",
                  "description": "A brief explanation of what the file change does or why it's being made."
                },
                "command": {
                  "type": "string",
                  "description": "The commands to run. Allowed options are: `create`, `str_replace`, `insert`, `append`.",
                  "enum": [
                    "create",
                    "str_replace",
                    "insert",
                    "append"
                  ]
                },
                "path": {
                  "description": "Absolute path to file or directory, e.g. `/repo/file.py` or `/repo`.",
                  "type": "string"
                },
                "new_str": {
                  "description": "Required parameter of `str_replace` command containing the new string. Required parameter of `insert` command containing the string to insert. Required parameter of `append` command containing the content to append to the file.",
                  "type": "string"
                },
                "file_text": {
                  "description": "Required parameter of `create` command, with the content of the file to be created.",
                  "type": "string"
                }
              }
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "use_aws",
          "description": "Make an AWS CLI api call with the specified service, operation, and parameters. All arguments MUST conform to the AWS CLI specification. Should the output of the invocation indicate a malformed command, invoke help to obtain the the correct command.",
          "input_schema": {
            "json": {
              "type": "object",
              "properties": {
                "label": {
                  "type": "string",
                  "description": "Human readable description of the api that is being called."
                },
                "service_name": {
                  "description": "The name of the AWS service. If you want to query s3, you should use s3api if possible.",
                  "type": "string"
                },
                "operation_name": {
                  "type": "string",
                  "description": "The name of the operation to perform."
                },
                "parameters": {
                  "description": "The parameters for the operation. The parameter keys MUST conform to the AWS CLI specification. You should prefer to use JSON Syntax over shorthand syntax wherever possible. For parameters that are booleans, prioritize using flags with no value. Denote these flags with flag names as key and an empty string as their value. You should also prefer kebab case.",
                  "type": "object"
                },
                "region": {
                  "description": "Region name for calling the operation on AWS.",
                  "type": "string"
                },
                "profile_name": {
                  "description": "Optional: AWS profile name to use from ~/.aws/credentials. Defaults to default profile if not specified.",
                  "type": "string"
                }
              },
              "required": [
                "region",
                "service_name",
                "operation_name",
                "label"
              ]
            }
          }
        }
      }
    ],
    "awslabsaws_diagram_mcp_server": [
      {
        "ToolSpecification": {
          "name": "awslabsaws_diagram_mcp_server___get_diagram_examples",
          "description": "Get example code for different types of diagrams.\n\n    This tool provides ready-to-use example code for various diagram types.\n    Use these examples to understand the syntax and capabilities of the diagrams package\n    before creating your own custom diagrams.\n\n    USAGE INSTRUCTIONS:\n    1. Select the diagram type you're interested in (or 'all' to see all examples)\n    2. Study the returned examples to understand the structure and syntax\n    3. Use these examples as templates for your own diagrams\n    4. When ready, modify an example or write your own code and use generate_diagram\n\n    EXAMPLE CATEGORIES:\n    - aws: AWS cloud architecture diagrams (basic services, grouped workers, clustered web services, Bedrock)\n    - sequence: Process and interaction flow diagrams\n    - flow: Decision trees and workflow diagrams\n    - class: Object relationship and inheritance diagrams\n    - k8s: Kubernetes architecture diagrams\n    - onprem: On-premises infrastructure diagrams\n    - custom: Custom diagrams with custom icons\n    - all: All available examples across categories\n\n    Each example demonstrates different features of the diagrams package:\n    - Basic connections between components\n    - Grouping with Clusters\n    - Advanced styling with Edge attributes\n    - Different layout directions\n    - Multiple component instances\n    - Custom icons and nodes\n\n    Parameters:\n        diagram_type (str): Type of diagram example to return. Options: aws, sequence, flow, class, k8s, onprem, custom, all\n\n    Returns:\n        Dictionary with example code for the requested diagram type(s), organized by example name\n    ",
          "input_schema": {
            "json": {
              "properties": {
                "diagram_type": {
                  "default": "all",
                  "description": "Type of diagram example to return. Options: aws, sequence, flow, class, k8s, onprem, custom, all",
                  "$ref": "#/$defs/DiagramType"
                }
              },
              "type": "object",
              "title": "mcp_get_diagram_examplesArguments",
              "$defs": {
                "DiagramType": {
                  "title": "DiagramType",
                  "type": "string",
                  "description": "Enum for supported diagram types.",
                  "enum": [
                    "aws",
                    "sequence",
                    "flow",
                    "class",
                    "k8s",
                    "onprem",
                    "custom",
                    "all"
                  ]
                }
              }
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "awslabsaws_diagram_mcp_server___list_icons",
          "description": "List available icons from the diagrams package, with optional filtering.\n\n    This tool dynamically inspects the diagrams package to find available\n    providers, services, and icons that can be used in diagrams.\n\n    USAGE INSTRUCTIONS:\n    1. Call without filters to get a list of available providers\n    2. Call with provider_filter to get all services and icons for that provider\n    3. Call with both provider_filter and service_filter to get icons for a specific service\n\n    Example workflow:\n    - First call: list_icons() → Returns all available providers\n    - Second call: list_icons(provider_filter=\"aws\") → Returns all AWS services and icons\n    - Third call: list_icons(provider_filter=\"aws\", service_filter=\"compute\") → Returns AWS compute icons\n\n    This approach is more efficient than loading all icons at once, especially when you only need\n    icons from specific providers or services.\n\n    Returns:\n        Dictionary with available providers, services, and icons organized hierarchically\n    ",
          "input_schema": {
            "json": {
              "properties": {
                "service_filter": {
                  "anyOf": [
                    {
                      "type": "string"
                    },
                    {
                      "type": "null"
                    }
                  ],
                  "default": null,
                  "description": "Filter icons by service name (e.g., \"compute\", \"database\", \"network\")",
                  "title": "Service Filter"
                },
                "provider_filter": {
                  "title": "Provider Filter",
                  "default": null,
                  "description": "Filter icons by provider name (e.g., \"aws\", \"gcp\", \"k8s\")",
                  "anyOf": [
                    {
                      "type": "string"
                    },
                    {
                      "type": "null"
                    }
                  ]
                }
              },
              "title": "mcp_list_diagram_iconsArguments",
              "type": "object"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "awslabsaws_diagram_mcp_server___generate_diagram",
          "description": "Generate a diagram from Python code using the diagrams package.\n\n    This tool accepts Python code as a string that uses the diagrams package DSL\n    and generates a PNG diagram without displaying it. The code is executed with\n    show=False to prevent automatic display.\n\n    USAGE INSTRUCTIONS:\n    Never import. Start writing code immediately with `with Diagram(` and use the icons you found with list_icons.\n    1. First use get_diagram_examples to understand the syntax and capabilities\n    2. Then use list_icons to discover all available icons. These are the only icons you can work with.\n    3. You MUST use icon names exactly as they are in the list_icons response, case-sensitive.\n    4. Write your diagram code following python diagrams examples. Do not import any additional icons or packages, the runtime already imports everything needed.\n    5. Submit your code to this tool to generate the diagram\n    6. The tool returns the path to the generated PNG file\n    7. For complex diagrams, consider using Clusters to organize components\n    8. Diagrams should start with a user or end device on the left, with data flowing to the right.\n\n    CODE REQUIREMENTS:\n    - Must include a Diagram() definition with appropriate parameters\n    - Can use any of the supported diagram components (AWS, K8s, etc.)\n    - Can include custom styling with Edge attributes (color, style)\n    - Can use Cluster to group related components\n    - Can use custom icons with the Custom class\n\n    COMMON PATTERNS:\n    - Basic: provider.service(\"label\")\n    - Connections: service1 >> service2 >> service3\n    - Grouping: with Cluster(\"name\"): [components]\n    - Styling: service1 >> Edge(color=\"red\", style=\"dashed\") >> service2\n\n    IMPORTANT FOR CLINE: Always send the current workspace directory when calling this tool!\n    The workspace_dir parameter should be set to the directory where the user is currently working\n    so that diagrams are saved to a location accessible to the user.\n\n    Supported diagram types:\n    - AWS architecture diagrams\n    - Sequence diagrams\n    - Flow diagrams\n    - Class diagrams\n    - Kubernetes diagrams\n    - On-premises diagrams\n    - Custom diagrams with custom nodes\n\n    Returns:\n        Dictionary with the path to the generated diagram and status information\n    ",
          "input_schema": {
            "json": {
              "properties": {
                "workspace_dir": {
                  "default": null,
                  "title": "Workspace Dir",
                  "description": "The user's current workspace directory. CRITICAL: Client must always send the current workspace directory when calling this tool! If provided, diagrams will be saved to a 'generated-diagrams' subdirectory.",
                  "anyOf": [
                    {
                      "type": "string"
                    },
                    {
                      "type": "null"
                    }
                  ]
                },
                "timeout": {
                  "default": 90,
                  "title": "Timeout",
                  "description": "The timeout for diagram generation in seconds. Default is 90 seconds.",
                  "type": "integer"
                },
                "code": {
                  "description": "Python code using the diagrams package DSL. The runtime already imports everything needed so you can start immediately using `with Diagram(`",
                  "title": "Code",
                  "type": "string"
                },
                "filename": {
                  "title": "Filename",
                  "default": null,
                  "description": "The filename to save the diagram to. If not provided, a random name will be generated.",
                  "anyOf": [
                    {
                      "type": "string"
                    },
                    {
                      "type": "null"
                    }
                  ]
                }
              },
              "required": [
                "code"
              ],
              "type": "object",
              "title": "mcp_generate_diagramArguments"
            }
          }
        }
      }
    ],
    "aws_cloudhsm_migration_tool": [
      {
        "ToolSpecification": {
          "name": "aws_cloudhsm_migration_tool___analyze_java_code",
          "description": "Analyze Java code for CloudHSM SDK migration issues\n\nArgs:\n    path: Path to Java code directory or file to analyze\n    output: Output file path for results (optional)\n    \nReturns:\n    Java analysis results with migration issues and recommendations",
          "input_schema": {
            "json": {
              "type": "object",
              "properties": {
                "path": {
                  "type": "string",
                  "title": "Path"
                },
                "output": {
                  "anyOf": [
                    {
                      "type": "string"
                    },
                    {
                      "type": "null"
                    }
                  ],
                  "title": "Output",
                  "default": null
                }
              },
              "required": [
                "path"
              ]
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "aws_cloudhsm_migration_tool___scan_aws_mock",
          "description": "Mock AWS scanning for development and testing\n\nArgs:\n    regions: Comma-separated AWS regions to mock scan\n    \nReturns:\n    Mock AWS scan results",
          "input_schema": {
            "json": {
              "type": "object",
              "properties": {
                "regions": {
                  "title": "Regions",
                  "default": "us-east-1",
                  "type": "string"
                }
              }
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "aws_cloudhsm_migration_tool___complete_migration_assessment",
          "description": "Complete end-to-end CloudHSM migration assessment workflow\n\nArgs:\n    regions: Comma-separated AWS regions to scan\n    java_path: Path to Java code to analyze (optional)\n    accounts: Comma-separated AWS account IDs (optional)\n    enhanced: Enable enhanced AWS scanning (default: True)\n    use_mock: Use mock data instead of real AWS scanning (default: False)\n    \nReturns:\n    Complete assessment results with summary and recommendations",
          "input_schema": {
            "json": {
              "required": [
                "regions"
              ],
              "properties": {
                "regions": {
                  "type": "string",
                  "title": "Regions"
                },
                "use_mock": {
                  "title": "Use Mock",
                  "default": false,
                  "type": "boolean"
                },
                "java_path": {
                  "default": null,
                  "anyOf": [
                    {
                      "type": "string"
                    },
                    {
                      "type": "null"
                    }
                  ],
                  "title": "Java Path"
                },
                "enhanced": {
                  "type": "boolean",
                  "default": true,
                  "title": "Enhanced"
                },
                "accounts": {
                  "anyOf": [
                    {
                      "type": "string"
                    },
                    {
                      "type": "null"
                    }
                  ],
                  "title": "Accounts",
                  "default": null
                }
              },
              "type": "object"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "aws_cloudhsm_migration_tool___scan_aws_environment",
          "description": "Comprehensive AWS environment scanning for CloudHSM installations using Python Unit 1\n\nArgs:\n    regions: Comma-separated AWS regions to scan (e.g., 'us-east-1,us-west-2')\n    accounts: Comma-separated AWS account IDs to scan (optional)\n    enhanced: Enable enhanced scanning with SSM commands (default: True)\n    \nReturns:\n    AWS environment scan results with CloudHSM installations",
          "input_schema": {
            "json": {
              "required": [
                "regions"
              ],
              "type": "object",
              "properties": {
                "regions": {
                  "type": "string",
                  "title": "Regions"
                },
                "enhanced": {
                  "type": "boolean",
                  "title": "Enhanced",
                  "default": true
                },
                "accounts": {
                  "anyOf": [
                    {
                      "type": "string"
                    },
                    {
                      "type": "null"
                    }
                  ],
                  "default": null,
                  "title": "Accounts"
                }
              }
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "aws_cloudhsm_migration_tool___check_aws_permissions",
          "description": "Check AWS permissions required for CloudHSM scanning\n\nArgs:\n    regions: Comma-separated AWS regions to check permissions for\n    \nReturns:\n    Permission check results",
          "input_schema": {
            "json": {
              "properties": {
                "regions": {
                  "default": "us-east-1",
                  "type": "string",
                  "title": "Regions"
                }
              },
              "type": "object"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "aws_cloudhsm_migration_tool___generate_migration_report",
          "description": "Generate comprehensive migration assessment report using Python Unit 1\n\nArgs:\n    aws_data_file: Path to AWS scan results JSON file\n    java_data_file: Path to Java analysis results JSON file (optional)\n    format: Output format (html, pdf, json, markdown)\n    output_dir: Directory to save generated reports\n    \nReturns:\n    Report generation results with file paths",
          "input_schema": {
            "json": {
              "type": "object",
              "properties": {
                "aws_data_file": {
                  "title": "Aws Data File",
                  "type": "string"
                },
                "output_dir": {
                  "type": "string",
                  "default": "reports",
                  "title": "Output Dir"
                },
                "format": {
                  "default": "markdown",
                  "title": "Format",
                  "type": "string"
                },
                "java_data_file": {
                  "anyOf": [
                    {
                      "type": "string"
                    },
                    {
                      "type": "null"
                    }
                  ],
                  "default": null,
                  "title": "Java Data File"
                }
              },
              "required": [
                "aws_data_file"
              ]
            }
          }
        }
      }
    ],
    "awslabscdk_mcp_server": [
      {
        "ToolSpecification": {
          "name": "awslabscdk_mcp_server___GetAwsSolutionsConstructPattern",
          "description": "Search and discover AWS Solutions Constructs patterns.\n\n    AWS Solutions Constructs are vetted architecture patterns that combine multiple\n    AWS services to solve common use cases following AWS Well-Architected best practices.\n\n    Key benefits:\n    - Accelerated Development: Implement common patterns without boilerplate code\n    - Best Practices Built-in: Security, reliability, and performance best practices\n    - Reduced Complexity: Simplified interfaces for multi-service architectures\n    - Well-Architected: Patterns follow AWS Well-Architected Framework principles\n\n    When to use Solutions Constructs:\n    - Implementing common architecture patterns (e.g., API + Lambda + DynamoDB)\n    - You want secure defaults and best practices applied automatically\n    - You need to quickly prototype or build production-ready infrastructure\n\n    This tool provides metadata about patterns. For complete documentation,\n    use the resource URI returned in the 'documentation_uri' field.\n\n    Args:\n        ctx: MCP context\n        pattern_name: Optional name of the specific pattern (e.g., 'aws-lambda-dynamodb')\n        services: Optional list of AWS services to search for patterns that use them\n                 (e.g., ['lambda', 'dynamodb'])\n\n    Returns:\n        Dictionary with pattern metadata including description, services, and documentation URI\n    ",
          "input_schema": {
            "json": {
              "type": "object",
              "title": "get_aws_solutions_construct_patternArguments",
              "properties": {
                "pattern_name": {
                  "default": null,
                  "anyOf": [
                    {
                      "type": "string"
                    },
                    {
                      "type": "null"
                    }
                  ],
                  "title": "Pattern Name"
                },
                "services": {
                  "default": null,
                  "anyOf": [
                    {
                      "type": "array",
                      "items": {
                        "type": "string"
                      }
                    },
                    {
                      "type": "null"
                    }
                  ],
                  "title": "Services"
                }
              }
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "awslabscdk_mcp_server___GenerateBedrockAgentSchema",
          "description": "Generate OpenAPI schema for Bedrock Agent Action Groups from a file.\n\n    This tool converts a Lambda file with BedrockAgentResolver into a Bedrock-compatible\n    OpenAPI schema. It uses a progressive approach to handle common issues:\n    1. Direct import of the Lambda file\n    2. Simplified version with problematic imports commented out\n    3. Fallback script generation if needed\n\n    Args:\n        ctx: MCP context\n        lambda_code_path: Path to Python file containing BedrockAgentResolver app\n        output_path: Where to save the generated schema\n\n    Returns:\n        Dictionary with schema generation results, including status, path to generated schema,\n        and diagnostic information if errors occurred\n    ",
          "input_schema": {
            "json": {
              "required": [
                "lambda_code_path",
                "output_path"
              ],
              "title": "bedrock_schema_generator_from_fileArguments",
              "properties": {
                "output_path": {
                  "type": "string",
                  "title": "Output Path"
                },
                "lambda_code_path": {
                  "type": "string",
                  "title": "Lambda Code Path"
                }
              },
              "type": "object"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "awslabscdk_mcp_server___CDKGeneralGuidance",
          "description": "Use this tool to get prescriptive CDK advice for building applications on AWS.\n\n    Args:\n        ctx: MCP context\n    ",
          "input_schema": {
            "json": {
              "type": "object",
              "title": "cdk_guidanceArguments",
              "properties": {}
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "awslabscdk_mcp_server___SearchGenAICDKConstructs",
          "description": "Search for GenAI CDK constructs by name or type.\n\n    The search is flexible and will match any of your search terms (OR logic).\n    It handles common variations like singular/plural forms and terms with/without spaces.\n    Content is fetched dynamically from GitHub to ensure the most up-to-date documentation.\n\n    Examples:\n    - \"bedrock agent\" - Returns all agent-related constructs\n    - \"knowledgebase vector\" - Returns knowledge base constructs related to vector stores\n    - \"agent actiongroups\" - Returns action groups for agents\n    - \"opensearch vector\" - Returns OpenSearch vector constructs\n\n    The search supports subdirectory content (like knowledge bases and their sections)\n    and will find matches across all available content.\n\n    Args:\n        ctx: MCP context\n        query: Search term(s) to find constructs by name or description\n        construct_type: Optional filter by construct type ('bedrock', 'opensearchserverless', etc.)\n\n    Returns:\n        Dictionary with matching constructs and resource URIs\n    ",
          "input_schema": {
            "json": {
              "title": "search_genai_cdk_constructsArguments",
              "properties": {
                "query": {
                  "title": "Query",
                  "default": null,
                  "anyOf": [
                    {
                      "type": "string"
                    },
                    {
                      "type": "null"
                    }
                  ]
                },
                "construct_type": {
                  "title": "Construct Type",
                  "anyOf": [
                    {
                      "type": "string"
                    },
                    {
                      "type": "null"
                    }
                  ],
                  "default": null
                }
              },
              "type": "object"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "awslabscdk_mcp_server___LambdaLayerDocumentationProvider",
          "description": "Provide documentation sources for Lambda layers.\n\n    This tool returns information about where to find documentation for Lambda layers\n    and instructs the MCP Client to fetch and process this documentation.\n\n    Args:\n        ctx: MCP context\n        layer_type: Type of layer (\"generic\" or \"python\")\n\n    Returns:\n        Dictionary with documentation source information\n    ",
          "input_schema": {
            "json": {
              "title": "lambda_layer_documentation_providerArguments",
              "type": "object",
              "required": [
                "layer_type"
              ],
              "properties": {
                "layer_type": {
                  "type": "string",
                  "title": "Layer Type"
                }
              }
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "awslabscdk_mcp_server___CheckCDKNagSuppressions",
          "description": "Check if CDK code contains Nag suppressions that require human review.\n\n    Scans TypeScript/JavaScript code for NagSuppressions usage to ensure security\n    suppressions receive proper human oversight and justification.\n\n    Args:\n        ctx: MCP context\n        code: CDK code to analyze (TypeScript/JavaScript)\n        file_path: Path to a file containing CDK code to analyze\n\n    Returns:\n        Analysis results with suppression details and security guidance\n    ",
          "input_schema": {
            "json": {
              "type": "object",
              "properties": {
                "code": {
                  "anyOf": [
                    {
                      "type": "string"
                    },
                    {
                      "type": "null"
                    }
                  ],
                  "default": null,
                  "title": "Code"
                },
                "file_path": {
                  "anyOf": [
                    {
                      "type": "string"
                    },
                    {
                      "type": "null"
                    }
                  ],
                  "default": null,
                  "title": "File Path"
                }
              },
              "title": "check_cdk_nag_suppressions_toolArguments"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "awslabscdk_mcp_server___ExplainCDKNagRule",
          "description": "Explain a specific CDK Nag rule with AWS Well-Architected guidance.\n\n    CDK Nag is a crucial tool for ensuring your CDK applications follow AWS security best practices.\n\n    Basic implementation:\n    ```typescript\n    import { App } from 'aws-cdk-lib';\n    import { AwsSolutionsChecks } from 'cdk-nag';\n\n    const app = new App();\n    // Create your stack\n    const stack = new MyStack(app, 'MyStack');\n    // Apply CDK Nag\n    AwsSolutionsChecks.check(app);\n    ```\n\n    Optional integration patterns:\n\n    1. Using environment variables:\n    ```typescript\n    if (process.env.ENABLE_CDK_NAG === 'true') {\n      AwsSolutionsChecks.check(app);\n    }\n    ```\n\n    2. Using CDK context parameters:\n    ```typescript\n    3. Environment-specific application:\n    ```typescript\n    const environment = app.node.tryGetContext('environment') || 'development';\n    if (['production', 'staging'].includes(environment)) {\n      AwsSolutionsChecks.check(stack);\n    }\n    ```\n\n    For more information on specific rule packs:\n    - Use resource `cdk-nag://rules/{rule_pack}` to get all rules for a specific pack\n    - Use resource `cdk-nag://warnings/{rule_pack}` to get warnings for a specific pack\n    - Use resource `cdk-nag://errors/{rule_pack}` to get errors for a specific pack\n\n    Args:\n        ctx: MCP context\n        rule_id: The CDK Nag rule ID (e.g., 'AwsSolutions-IAM4')\n\n    Returns:\n        Dictionary with detailed explanation and remediation steps\n    ",
          "input_schema": {
            "json": {
              "title": "explain_cdk_nag_ruleArguments",
              "required": [
                "rule_id"
              ],
              "type": "object",
              "properties": {
                "rule_id": {
                  "type": "string",
                  "title": "Rule Id"
                }
              }
            }
          }
        }
      }
    ],
    "amazon_internal_mcp_server": [
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___overleaf_clone_project",
          "description": "Clone an Overleaf project to the local workspace.\n\nThis tool clones the specified Overleaf project to the local workspace directory.\nThe project will be stored in ./overleaf/{project_id}.\nIf the project is already cloned locally, this operation is idempotent and will skip cloning.\n\nExample usage:\n```json\n{\n  \"project_id\": \"507f1f77bcf86cd799439011\"\n}\n```",
          "input_schema": {
            "json": {
              "properties": {
                "project_id": {
                  "type": "string",
                  "description": "Project ID to clone",
                  "pattern": "^[a-zA-Z0-9_-]+$"
                }
              },
              "$schema": "http://json-schema.org/draft-07/schema#",
              "type": "object",
              "required": [
                "project_id"
              ],
              "additionalProperties": false
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___andes_table",
          "description": "Access and manage Andes tables and their versions.",
          "input_schema": {
            "json": {
              "additionalProperties": false,
              "properties": {
                "limit": {
                  "type": "number",
                  "description": "Maximum number of results to return"
                },
                "providerId": {
                  "type": "string",
                  "description": "ID of the provider"
                },
                "operation": {
                  "enum": [
                    "list_tables",
                    "get_table_details",
                    "list_table_versions",
                    "get_table_version_details",
                    "get_table_version_schema"
                  ],
                  "type": "string",
                  "description": "The table operation to perform"
                },
                "tableName": {
                  "type": "string",
                  "description": "Name of the table (required for table-specific operations)"
                },
                "versionNumber": {
                  "type": "string",
                  "description": "Version number (required for version-specific operations)"
                },
                "showDeleted": {
                  "type": "boolean",
                  "description": "Whether to include deleted tables in results"
                },
                "marker": {
                  "description": "Token for pagination",
                  "type": "string"
                }
              },
              "$schema": "http://json-schema.org/draft-07/schema#",
              "required": [
                "operation",
                "providerId"
              ],
              "type": "object"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___lock_unlock_quip_document",
          "description": "Lock or unlock a Quip document\n\nThis tool allows you to lock or unlock a Quip document to control whether it can be edited.\nWhen a document is locked, users cannot make changes to it (except for the document owner and users with admin privileges).\n\nExample usage:\n```json\n{\n  \"threadIdOrUrl\": \"https://quip-amazon.com/abc/Doc\",\n  \"lock\": true\n}\n```\n\nTo unlock a document:\n```json\n{\n  \"threadIdOrUrl\": \"https://quip-amazon.com/abc/Doc\",\n  \"lock\": false\n}\n```\n\nNote: You must have appropriate permissions to lock or unlock a document.",
          "input_schema": {
            "json": {
              "$schema": "http://json-schema.org/draft-07/schema#",
              "additionalProperties": false,
              "properties": {
                "threadIdOrUrl": {
                  "description": "The thread ID or Quip URL of the document to lock or unlock",
                  "type": "string"
                },
                "lock": {
                  "description": "Tick the checkbox to lock or uncheck to unlock the document",
                  "type": "boolean"
                }
              },
              "type": "object",
              "required": [
                "threadIdOrUrl",
                "lock"
              ]
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___lookup_team_code_resource",
          "description": "Looks up code artifacts, such as packages, version sets a given team",
          "input_schema": {
            "json": {
              "required": [
                "team"
              ],
              "properties": {
                "team": {
                  "type": "string",
                  "description": "Bindle team as represented in https://permissions.amazon.com/a/team/{team}"
                }
              },
              "type": "object",
              "$schema": "http://json-schema.org/draft-07/schema#",
              "additionalProperties": false
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___read_internal_website",
          "description": "Read content from internal Amazon websites.\n\nSupported websites and their purposes:\n\nDocumentation & Knowledge:\n- docs.hub.amazon.dev: Internal technical documentation\n- hub.cx.aws.dev: Internal technical documentation for building an experience in the AWS Management Console\n- btdocs.builder-tools.aws.dev: BuilderHub contributor documentation\n- docs.ctps.amazon.dev: CTPS technical documentation\n- docs.paystation.amazon.dev: PayStation technical documentation\n- skb.highcastle.a2z: Security knowledge base docs\n- aristotle.a2z.com: AWS Security Knowledge Base Docs\n- docs.aws.amazon.com: External AWS documentation\n- documentation.skynet.aws.dev: Skynet documentation\n- sage.amazon.dev: Engineering Q&A platform\n- datacentral.a2z.com/cradle: DataCentral Cradle job runs\n- oldfart.tools.amazon.dev: Important user tenure information and cohort statistics\n- sidekick.aka.amazon.com: Help users perform redundant tasks of aggregating trouble ticket or SIM data by creating custom oncall reports\n\nDocument Storage & Sharing:\n- workdocs.amazon.com: Amazon WorkDocs (PDFs, Word Docs, Excel)\n- drive-render.corp.amazon.com: Amazon Drive content\n- quip-amazon.com: Collaborative documents\n- paste.amazon.com: Raw content sharing\n- w.amazon.com: Internal MediaWiki\n- noogle-eu.amazon.com: Noogle EU customer information system\n- noogle-na.amazon.com: Noogle NA customer information system\n- noogle-fe.amazon.com: Noogle FE customer information system\n- apttool.amazon.com: Weblab APT report\n- confluence.collab.games.aws.dev: Amazon Games internal confluence page\n\nDevelopment & Build Tools:\n- code.amazon.com: Internal code repository\n- build.amazon.com: Build fleet and net-gapped builds\n- pipelines.amazon.com: Pipeline information\n- tod.amazon.com: TOD Test run information\n- apollo.amazon.com: Apollo Environment information\n- artifact-browser.brazil.aws.dev: Artifact content browser\n- bindles.amazon.com: Permissions information\n- katal.amazon.dev: UI Components library named Katal (via CloudFront presigned URLs)\n- digicon.amazon.com: Digital Order Console for order information\n- grass-*.aka.amazon.com: Grass - Primary tool for exploring Ordering data (NA, EU, FE, CN regions)\n- grass.integ.amazon.com: Grass Integration environment for testing\n- cloudscape.aws.dev: Internal Cloudscape System Design documentation\n\nProject Management & Tickets:\n- taskei.amazon.dev: Task and project management, manage tasks, sprints, kanban boards, planning and scrum processes.\n- t.corp.amazon.com: Ticket system to manage urgent work through severity, routed based on CTI.\n- sim.amazon.com: Legacy issue management system. Used to manage Issues.\n- issues.amazon.com: Legacy issue management system. Used to manage Issues.\n- mcm.amazon.dev: Manual-change-management checklists\n- retro.corp.amazon.com: Sprint retrospectives\n- board.amazon.com: Organize tasks in cards in a board\n- kingpin.amazon.com: Amazon's internal system for managing and reporting goals\n- weblab.amazon.com: Weblab experiment details, configuration settings, and any weblabs flagged as risks.\n\nSecurity & Operations:\n- myappsecdashboard.corp.amazon.com: AppSec affinity contacts\n- cti.amazon.com: CTI and resolver group information\n- design-inspector.a2z.com: Design diagrams and threat models\n- redfort.amazon.com: Public Key Infrastructure for Amazon\n- f2p-visualizer.corp.amazon.com: F2P (Fulfill-to-Promise) visualizer for Amazon order planning information such as https://f2p-visualizer.corp.amazon.com/export/($ORDER_ID)\n- marts-gfs-ui-finuat.corp.amazon.com: MARTS (General AR Invoice Status Dashboard for FINUAT)\n- theauditor.amazon.com: LTRA (Lite Technical Risk Assessment) audit information\n\nTeam & Organization:\n- phonetool.amazon.com: Employee roster and details\n\nMedia & Communications:\n- broadcast.amazon.com: Internal broadcasts and videos with transcripts\n\nPolicy Documents:\n- policy.a2z.com: Amazon internal policy documents\nMonitoring\n- monitorportal.amazon.com: iGraph tool\n- carnaval.amazon.com: Monitoring and alarm management\n- deeops.aka.amazon.com: DeeOps STO Health monitoring for user statistics including current over SLA tickets, incoming/open/resolved tickets, MTTR, and ticket age metrics\n- lyrebird.corp.amazon.com: Lyrebird test reports and traffic test details\n\nAnalytics & Dashboards:\n- quicksight.aws.amazon.com: Amazon QuickSight dashboards and analytics\n\nConcurrency Control:\n- This tool supports processing multiple URLs concurrently with a configurable concurrency limit",
          "input_schema": {
            "json": {
              "type": "object",
              "$schema": "http://json-schema.org/draft-07/schema#",
              "additionalProperties": false,
              "properties": {
                "tailingLineCount": {
                  "description": "Number of most recent log lines to return",
                  "type": "number"
                },
                "concurrencyLimit": {
                  "description": "Maximum number of concurrent requests",
                  "type": "number"
                },
                "urls": {
                  "type": "array",
                  "items": {
                    "format": "uri",
                    "type": "string"
                  },
                  "description": "Array of internal website URLs to read. Multiple URLs will be processed concurrently based on the concurrencyLimit parameter."
                },
                "url": {
                  "type": "string",
                  "format": "uri",
                  "description": "URL of the internal website to read. For backward compatibility with older clients."
                },
                "useGenericStrategy": {
                  "description": "Use generic HTML to Markdown conversion instead of specific matchers",
                  "type": "boolean",
                  "default": false
                }
              }
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___search_products",
          "description": "Search for products on Amazon.com (US marketplace only) and extract structured product information including titles, prices, ratings, and images",
          "input_schema": {
            "json": {
              "properties": {
                "maxResults": {
                  "type": "number",
                  "description": "Maximum number of products to return (default: 10, max recommended: 50)"
                },
                "filters": {
                  "additionalProperties": false,
                  "type": "object",
                  "properties": {
                    "index": {
                      "description": "Department to search in. Available options include: 'all' (default), 'books', 'electronics', 'computers', 'clothing', 'home', 'beauty', 'toys', 'grocery', 'sports', 'automotive', 'pets', 'baby', 'health', 'industrial', 'movies', 'music', 'video-games', 'tools', 'office-products', and more",
                      "type": "string"
                    },
                    "maxPrice": {
                      "description": "Maximum price filter in dollars (e.g., 100 for $100)",
                      "type": "number"
                    },
                    "minPrice": {
                      "description": "Minimum price filter in dollars (e.g., 25 for $25)",
                      "type": "number"
                    },
                    "sortBy": {
                      "description": "Sort order for results. Available options include:\n- 'relevanceblender' (default): Sort by relevance\n- 'price-asc-rank': Price low to high\n- 'price-desc-rank': Price high to low\n- 'review-rank': Average customer review\n- 'date-desc-rank': Newest arrivals\n- 'exact-aware-popularity-rank': Popularity\n- 'get-it-fast-rank': Fastest delivery\n- 'low-prices-rank': Lowest price with ranking factors\n- 'most-purchased-rank': Most purchased\n- 'top-brands-rank': Top brands",
                      "type": "string"
                    }
                  },
                  "description": "Optional filters to narrow down search results"
                },
                "query": {
                  "type": "string",
                  "description": "Search query string for the products you want to find"
                }
              },
              "type": "object",
              "$schema": "http://json-schema.org/draft-07/schema#",
              "required": [
                "query"
              ],
              "additionalProperties": false
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___plantuml",
          "description": "Create and decode PlantUML diagrams using Amazon's internal PlantUML server.\nPlantUML allows creating UML diagrams from text descriptions.\n\nSupported operations:\n- encode: Convert PlantUML text to an encoded URL\n- decode: Extract PlantUML text from an encoded URL",
          "input_schema": {
            "json": {
              "$schema": "http://json-schema.org/draft-07/schema#",
              "properties": {
                "url": {
                  "format": "uri",
                  "type": "string",
                  "description": "PlantUML URL for decode operation"
                },
                "content": {
                  "description": "PlantUML content for encode operation",
                  "type": "string"
                },
                "operation": {
                  "description": "The operation to perform",
                  "type": "string",
                  "enum": [
                    "encode",
                    "decode"
                  ]
                }
              },
              "type": "object",
              "required": [
                "operation"
              ],
              "additionalProperties": false
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___jira_get_attachment",
          "description": "Download an attachment from a JIRA issue",
          "input_schema": {
            "json": {
              "additionalProperties": false,
              "type": "object",
              "properties": {
                "attachmentUrl": {
                  "type": "string",
                  "minLength": 1,
                  "description": "The URL of the attachment to download"
                },
                "outputPath": {
                  "type": "string",
                  "description": "Path where to save the downloaded attachment"
                }
              },
              "required": [
                "attachmentUrl"
              ],
              "$schema": "http://json-schema.org/draft-07/schema#"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___pippin_get_project",
          "description": "Retrieves a Pippin design project by its ID",
          "input_schema": {
            "json": {
              "type": "object",
              "properties": {
                "projectId": {
                  "type": "string",
                  "description": "Project ID"
                }
              },
              "required": [
                "projectId"
              ],
              "additionalProperties": false,
              "$schema": "http://json-schema.org/draft-07/schema#"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___g2s2_create_stage_version",
          "description": "Creates a new stage version in G2S2 with the specified parent stage version",
          "input_schema": {
            "json": {
              "type": "object",
              "required": [
                "stageVersion",
                "parentStageVersion"
              ],
              "additionalProperties": false,
              "$schema": "http://json-schema.org/draft-07/schema#",
              "properties": {
                "parentStageVersion": {
                  "type": "string",
                  "description": "The parent stage version for the stage version"
                },
                "stageVersion": {
                  "description": "The stage version to create",
                  "type": "string"
                }
              }
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___pippin_update_artifact",
          "description": "Updates an existing artifact within a Pippin project",
          "input_schema": {
            "json": {
              "additionalProperties": false,
              "type": "object",
              "properties": {
                "projectId": {
                  "type": "string",
                  "description": "Project ID"
                },
                "designId": {
                  "description": "Artifact ID",
                  "type": "string"
                },
                "name": {
                  "description": "Updated artifact name",
                  "type": "string"
                },
                "description": {
                  "description": "Updated artifact description",
                  "type": "string"
                },
                "contentPath": {
                  "type": "string",
                  "description": "Path to a file containing the artifact content (provide this OR content)"
                },
                "content": {
                  "description": "Updated artifact content (provide this OR contentPath)",
                  "type": "string"
                }
              },
              "$schema": "http://json-schema.org/draft-07/schema#",
              "required": [
                "projectId",
                "designId"
              ]
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___search_MCMs",
          "description": "Search and filter Change Management (CM) records by various criteria:\n        • Personnel: requesters, technicians, resolver groups\n        • Status: CM status and closure codes\n        • Time-based: creation, updates, scheduling, and execution dates\n        • Results: configurable result limits",
          "input_schema": {
            "json": {
              "type": "object",
              "additionalProperties": false,
              "$schema": "http://json-schema.org/draft-07/schema#",
              "properties": {
                "cmOwnerCtiResolverGroup": {
                  "items": {
                    "description": "List of Resolver groups for the CMs",
                    "type": "string"
                  },
                  "type": "array"
                },
                "scheduledEnd": {
                  "description": "the scheduled end of the cm",
                  "additionalProperties": false,
                  "type": "object",
                  "properties": {
                    "lessThan": {
                      "properties": {
                        "value": {
                          "type": "number"
                        }
                      },
                      "additionalProperties": false,
                      "required": [
                        "value"
                      ],
                      "type": "object",
                      "description": "provide this predicate to find Cms that have scheduled end time less than the given value"
                    },
                    "between": {
                      "description": "provide this predicate to find Cms that have scheduled end time between the two values",
                      "properties": {
                        "end": {
                          "type": "number"
                        },
                        "start": {
                          "type": "number"
                        }
                      },
                      "required": [
                        "start",
                        "end"
                      ],
                      "type": "object",
                      "additionalProperties": false
                    },
                    "greaterThanOrEqualTo": {
                      "type": "object",
                      "properties": {
                        "value": {
                          "type": "number"
                        }
                      },
                      "additionalProperties": false,
                      "description": "provide this predicate to find Cms that have scheduled end time greater than or equal to the given value",
                      "required": [
                        "value"
                      ]
                    },
                    "lessThanOrEqualTo": {
                      "additionalProperties": false,
                      "properties": {
                        "value": {
                          "type": "number"
                        }
                      },
                      "description": "provide this predicate to find Cms that have scheduled end time less than or equal to the given value",
                      "required": [
                        "value"
                      ],
                      "type": "object"
                    },
                    "greaterThan": {
                      "additionalProperties": false,
                      "description": "provide this predicate to find Cms that have scheduled end time greater than the given value",
                      "properties": {
                        "value": {
                          "type": "number"
                        }
                      },
                      "type": "object",
                      "required": [
                        "value"
                      ]
                    }
                  }
                },
                "technician": {
                  "type": "array",
                  "items": {
                    "type": "string",
                    "description": "List of technicians of the CMs"
                  }
                },
                "requesters": {
                  "items": {
                    "description": "List of requesters of the CMs",
                    "type": "string"
                  },
                  "type": "array"
                },
                "updatedAt": {
                  "additionalProperties": false,
                  "description": "the time the Cm was updated",
                  "type": "object",
                  "properties": {
                    "between": {
                      "properties": {
                        "end": {
                          "type": "number"
                        },
                        "start": {
                          "type": "number"
                        }
                      },
                      "type": "object",
                      "description": "provide this predicate to find Cms that have updated at time between the two values",
                      "required": [
                        "start",
                        "end"
                      ],
                      "additionalProperties": false
                    },
                    "lessThanOrEqualTo": {
                      "required": [
                        "value"
                      ],
                      "additionalProperties": false,
                      "type": "object",
                      "properties": {
                        "value": {
                          "type": "number"
                        }
                      },
                      "description": "provide this predicate to find Cms that have updated at time less than or equal to the given value"
                    },
                    "greaterThan": {
                      "type": "object",
                      "properties": {
                        "value": {
                          "type": "number"
                        }
                      },
                      "required": [
                        "value"
                      ],
                      "additionalProperties": false,
                      "description": "provide this predicate to find Cms that have updated at time greater than the given value"
                    },
                    "lessThan": {
                      "properties": {
                        "value": {
                          "type": "number"
                        }
                      },
                      "additionalProperties": false,
                      "type": "object",
                      "description": "provide this predicate to find Cms that have updated at time less than the given value",
                      "required": [
                        "value"
                      ]
                    },
                    "greaterThanOrEqualTo": {
                      "properties": {
                        "value": {
                          "type": "number"
                        }
                      },
                      "description": "provide this predicate to find Cms that have updated at time greater than or equal to the given value",
                      "type": "object",
                      "required": [
                        "value"
                      ],
                      "additionalProperties": false
                    }
                  }
                },
                "actualEnd": {
                  "type": "object",
                  "properties": {
                    "greaterThanOrEqualTo": {
                      "type": "object",
                      "properties": {
                        "value": {
                          "type": "number"
                        }
                      },
                      "additionalProperties": false,
                      "required": [
                        "value"
                      ],
                      "description": "provide this predicate to find Cms that have actual end time greater than or equal to the given value"
                    },
                    "lessThan": {
                      "properties": {
                        "value": {
                          "type": "number"
                        }
                      },
                      "description": "provide this predicate to find Cms that have actual end time less than the given value",
                      "type": "object",
                      "required": [
                        "value"
                      ],
                      "additionalProperties": false
                    },
                    "between": {
                      "required": [
                        "start",
                        "end"
                      ],
                      "type": "object",
                      "properties": {
                        "start": {
                          "type": "number"
                        },
                        "end": {
                          "type": "number"
                        }
                      },
                      "description": "provide this predicate to find Cms that have actual end time between the two values",
                      "additionalProperties": false
                    },
                    "lessThanOrEqualTo": {
                      "required": [
                        "value"
                      ],
                      "properties": {
                        "value": {
                          "type": "number"
                        }
                      },
                      "additionalProperties": false,
                      "description": "provide this predicate to find Cms that have actual end time less than or equal to the given value",
                      "type": "object"
                    },
                    "greaterThan": {
                      "properties": {
                        "value": {
                          "type": "number"
                        }
                      },
                      "type": "object",
                      "additionalProperties": false,
                      "required": [
                        "value"
                      ],
                      "description": "provide this predicate to find Cms that have actual end time greater than the given value"
                    }
                  },
                  "additionalProperties": false,
                  "description": "the actual end of the cm"
                },
                "numResults": {
                  "description": "Number of results to return",
                  "type": "number",
                  "default": 100
                },
                "cmStatus": {
                  "description": "the status of the Cm",
                  "type": "array",
                  "items": {
                    "type": "string",
                    "enum": [
                      "Draft",
                      "PendingApproval",
                      "Scheduled",
                      "Modified",
                      "Rejected",
                      "Cancelled",
                      "Completed",
                      "Paused",
                      "Aborted",
                      "Discarded",
                      "Rework Required",
                      "Scheduled with Comments",
                      "In Progress",
                      "Pending Reapproval",
                      "Modified after Execution",
                      "Pending Reapproval after Execution",
                      "Preflight"
                    ]
                  }
                },
                "createdAt": {
                  "description": "the time the Cm was created",
                  "type": "object",
                  "additionalProperties": false,
                  "properties": {
                    "greaterThan": {
                      "additionalProperties": false,
                      "type": "object",
                      "required": [
                        "value"
                      ],
                      "description": "provide this predicate to find Cms that have created at time greater than the given value",
                      "properties": {
                        "value": {
                          "type": "number"
                        }
                      }
                    },
                    "lessThanOrEqualTo": {
                      "additionalProperties": false,
                      "description": "provide this predicate to find Cms that have created at time less than or equal to the given value",
                      "type": "object",
                      "properties": {
                        "value": {
                          "type": "number"
                        }
                      },
                      "required": [
                        "value"
                      ]
                    },
                    "greaterThanOrEqualTo": {
                      "description": "provide this predicate to find Cms that have created at time greater than or equal to the given value",
                      "properties": {
                        "value": {
                          "type": "number"
                        }
                      },
                      "required": [
                        "value"
                      ],
                      "additionalProperties": false,
                      "type": "object"
                    },
                    "lessThan": {
                      "required": [
                        "value"
                      ],
                      "additionalProperties": false,
                      "type": "object",
                      "properties": {
                        "value": {
                          "type": "number"
                        }
                      },
                      "description": "provide this predicate to find Cms that have created at time less than the given value"
                    },
                    "between": {
                      "properties": {
                        "start": {
                          "type": "number"
                        },
                        "end": {
                          "type": "number"
                        }
                      },
                      "type": "object",
                      "additionalProperties": false,
                      "description": "provide this predicate to find Cms that have created at time between the two values",
                      "required": [
                        "start",
                        "end"
                      ]
                    }
                  }
                },
                "scheduledStart": {
                  "type": "object",
                  "properties": {
                    "lessThanOrEqualTo": {
                      "additionalProperties": false,
                      "type": "object",
                      "properties": {
                        "value": {
                          "type": "number"
                        }
                      },
                      "description": "provide this predicate to find Cms that have scheduled end time less than or equal to the given value",
                      "required": [
                        "value"
                      ]
                    },
                    "between": {
                      "required": [
                        "start",
                        "end"
                      ],
                      "additionalProperties": false,
                      "type": "object",
                      "properties": {
                        "start": {
                          "type": "number"
                        },
                        "end": {
                          "type": "number"
                        }
                      },
                      "description": "provide this predicate to find Cms that have scheduled end time between the two values"
                    },
                    "greaterThan": {
                      "properties": {
                        "value": {
                          "type": "number"
                        }
                      },
                      "type": "object",
                      "additionalProperties": false,
                      "required": [
                        "value"
                      ],
                      "description": "provide this predicate to find Cms that have scheduled end time greater than the given value"
                    },
                    "lessThan": {
                      "required": [
                        "value"
                      ],
                      "additionalProperties": false,
                      "properties": {
                        "value": {
                          "type": "number"
                        }
                      },
                      "description": "provide this predicate to find Cms that have scheduled end time less than the given value",
                      "type": "object"
                    },
                    "greaterThanOrEqualTo": {
                      "required": [
                        "value"
                      ],
                      "description": "provide this predicate to find Cms that have scheduled end time greater than or equal to the given value",
                      "additionalProperties": false,
                      "type": "object",
                      "properties": {
                        "value": {
                          "type": "number"
                        }
                      }
                    }
                  },
                  "additionalProperties": false,
                  "description": "the scheduled start of the cm"
                },
                "actualStart": {
                  "type": "object",
                  "properties": {
                    "greaterThanOrEqualTo": {
                      "properties": {
                        "value": {
                          "type": "number"
                        }
                      },
                      "required": [
                        "value"
                      ],
                      "additionalProperties": false,
                      "type": "object",
                      "description": "provide this predicate to find Cms that have actual start time greater than or equal to the given value"
                    },
                    "between": {
                      "properties": {
                        "start": {
                          "type": "number"
                        },
                        "end": {
                          "type": "number"
                        }
                      },
                      "required": [
                        "start",
                        "end"
                      ],
                      "description": "provide this predicate to find Cms that have actual start time between the two values",
                      "additionalProperties": false,
                      "type": "object"
                    },
                    "greaterThan": {
                      "additionalProperties": false,
                      "type": "object",
                      "description": "provide this predicate to find Cms that have actual start time greater than the given value",
                      "properties": {
                        "value": {
                          "type": "number"
                        }
                      },
                      "required": [
                        "value"
                      ]
                    },
                    "lessThanOrEqualTo": {
                      "description": "provide this predicate to find Cms that have actual start time less than or equal to the given value",
                      "properties": {
                        "value": {
                          "type": "number"
                        }
                      },
                      "type": "object",
                      "required": [
                        "value"
                      ],
                      "additionalProperties": false
                    },
                    "lessThan": {
                      "properties": {
                        "value": {
                          "type": "number"
                        }
                      },
                      "additionalProperties": false,
                      "type": "object",
                      "required": [
                        "value"
                      ],
                      "description": "provide this predicate to find Cms that have actual start time less than the given value"
                    }
                  },
                  "additionalProperties": false,
                  "description": "the actual start of the cm"
                },
                "closureCode": {
                  "type": "array",
                  "items": {
                    "type": "string",
                    "enum": [
                      "Successful",
                      "Successful - Off Script",
                      "Unsuccessful"
                    ]
                  },
                  "description": "the closure code of the CMs"
                }
              }
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___overleaf_write_file",
          "description": "Write a file to an Overleaf project with automatic commit and push.\n\nThis tool writes content to the specified file in an Overleaf project.\nBefore writing, it ensures the project is cloned locally and synchronized.\nAfter writing, it automatically commits the changes with a descriptive message\nand pushes them to the remote repository.\n\nExample usage:\n```json\n{\n  \"project_id\": \"507f1f77bcf86cd799439011\",\n  \"file_path\": \"main.tex\",\n  \"content\": \"\\\\documentclass{article}\\n\\\\begin{document}\\nHello World\\n\\\\end{document}\"\n}\n```",
          "input_schema": {
            "json": {
              "properties": {
                "file_path": {
                  "description": "Path to the file within the project",
                  "type": "string"
                },
                "project_id": {
                  "type": "string",
                  "description": "Project ID to write to"
                },
                "content": {
                  "type": "string",
                  "description": "File content to write"
                }
              },
              "additionalProperties": false,
              "$schema": "http://json-schema.org/draft-07/schema#",
              "required": [
                "project_id",
                "file_path",
                "content"
              ],
              "type": "object"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___get_katal_component",
          "description": "Get detailed information about a specific Katal component\n\nThis tool retrieves comprehensive documentation and usage information for a given Katal component,\nincluding properties, methods, examples, guidelines, and accessibility information.\n\nExamples:\n1. Get Button component info:\n```json\n{\n  \"name\": \"Button\"\n}\n```",
          "input_schema": {
            "json": {
              "$schema": "http://json-schema.org/draft-07/schema#",
              "additionalProperties": false,
              "properties": {
                "name": {
                  "description": "Name of the Katal component to get information about",
                  "type": "string"
                }
              },
              "type": "object",
              "required": [
                "name"
              ]
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___pippin_create_project",
          "description": "Creates a new Pippin design project with specified details",
          "input_schema": {
            "json": {
              "additionalProperties": false,
              "$schema": "http://json-schema.org/draft-07/schema#",
              "required": [
                "name"
              ],
              "properties": {
                "requirements": {
                  "type": "string",
                  "description": "Project requirements"
                },
                "bindleId": {
                  "description": "Bindle ID",
                  "type": "string"
                },
                "name": {
                  "type": "string",
                  "description": "Project name"
                }
              },
              "type": "object"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___prompt_farm_prompt_content",
          "description": "A tool designed to fetch prompt content directly by specifying the repository name. This tool leverages repository identifiers to locate, extract, and deliver prompt templates or prompt from PromptFarm prompt repositories. It simplifies accessing prompt definitions without manual browsing, enabling users to quickly integrate or customize prompts by referencing the exact repository source.",
          "input_schema": {
            "json": {
              "required": [
                "repositoryName"
              ],
              "properties": {
                "repositoryName": {
                  "type": "string",
                  "description": "The name of the PromptFarm repository to retrieve the prompt from"
                }
              },
              "additionalProperties": false,
              "$schema": "http://json-schema.org/draft-07/schema#",
              "type": "object"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___jira_config_helper",
          "description": "Get help configuring JIRA tools for Q CLI",
          "input_schema": {
            "json": {
              "additionalProperties": false,
              "type": "object",
              "properties": {
                "token": {
                  "type": "string",
                  "description": "Your JIRA token (optional - for validation)"
                },
                "jira_url": {
                  "type": "string",
                  "description": "Your JIRA instance URL (optional - for validation)"
                }
              },
              "$schema": "http://json-schema.org/draft-07/schema#"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___list_katal_components",
          "description": "List all available Katal components\n\nThis tool returns a list of all available components in the Katal library,\norganized by category with basic information about each component.\n\nExample usage:\n```json\n{}\n```",
          "input_schema": {
            "json": {
              "properties": {},
              "$schema": "http://json-schema.org/draft-07/schema#",
              "additionalProperties": false,
              "type": "object"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___tod_download_logs",
          "description": "Download ToD logs to a file",
          "input_schema": {
            "json": {
              "additionalProperties": false,
              "type": "object",
              "properties": {
                "url": {
                  "description": "URL of the ToD test run",
                  "type": "string"
                },
                "outputPath": {
                  "description": "Custom output path for the log file",
                  "type": "string"
                },
                "timeoutMs": {
                  "type": "number",
                  "description": "Custom timeout in milliseconds (default: 5000)"
                }
              },
              "required": [
                "url"
              ],
              "$schema": "http://json-schema.org/draft-07/schema#"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___pippin_sync_project_to_remote",
          "description": "Synchronizes local files to a Pippin project as artifacts",
          "input_schema": {
            "json": {
              "$schema": "http://json-schema.org/draft-07/schema#",
              "type": "object",
              "properties": {
                "nameFormat": {
                  "enum": [
                    "use_filename",
                    "use_id"
                  ],
                  "description": "How to name artifacts",
                  "type": "string"
                },
                "projectId": {
                  "type": "string",
                  "description": "Project ID"
                },
                "inputDirectory": {
                  "description": "Local directory containing files to upload",
                  "type": "string"
                },
                "createMissing": {
                  "default": true,
                  "type": "boolean",
                  "description": "Create artifacts if they don't exist"
                }
              },
              "required": [
                "projectId",
                "inputDirectory"
              ],
              "additionalProperties": false
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___sim_get_issue",
          "description": "Get detailed information about a specific SIM issue.\nRetrieves full details of an issue including title, description, status, assignee, comments, and more.\nYou can use either the P-number (e.g., P12345678) or the alias (e.g., CFN-12345) as the issue ID.\nOptionally include a specific thread (e.g., 'Updates') to get its comments.\nSet includeCustomAttributes to true to fetch custom fields like Due Date, Metric Scope, etc.\nSet includeRelatedTasks to true to fetch parent and subtasks.\nsetExtensions to true to fetch extension metadata like estimated effort and points spent.",
          "input_schema": {
            "json": {
              "required": [
                "id"
              ],
              "$schema": "http://json-schema.org/draft-07/schema#",
              "additionalProperties": false,
              "type": "object",
              "properties": {
                "id": {
                  "type": "string",
                  "description": "Issue ID or alias (e.g., P12345678 or CFN-12345)"
                },
                "includeCustomAttributes": {
                  "type": "boolean",
                  "description": "Whether to include custom attributes like Due Date, Metric Scope, etc."
                },
                "includeRelatedTasks": {
                  "description": "Whether to include parent and subtasks",
                  "type": "boolean"
                },
                "includeExtensions": {
                  "description": "Whether to include extensions like estimated and spent points",
                  "type": "boolean"
                },
                "includeThread": {
                  "description": "Name of the thread to include (e.g., \"Updates\")",
                  "type": "string"
                }
              }
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___create_quip",
          "description": "Create a new Quip document or spreadsheet\n\nThis tool creates a new document or spreadsheet in Quip with the specified content.\n\nRequired parameters:\n- content: The HTML or Markdown content of the new document (max 1MB)\n\nOptional parameters:\n- format: Format of the content ('html' or 'markdown', default is 'html')\n- title: Title of the new document (max 10KB)\n- member_ids: Comma-separated list of folder IDs or user IDs for access\n- type: Type of document to create ('document' or 'spreadsheet', default is 'document')\n\nNotes:\n- If title is not specified, it will be inferred from the first content\n- If member_ids is not specified, the document will be created in the user's Private folder\n- For spreadsheets, content must be surrounded by HTML <table> tags\n\nExamples:\n1. Create a simple document:\n```json\n{\n  \"content\": \"# My New Document\\n\\nThis is a test document.\",\n  \"format\": \"markdown\"\n}\n```\n\n2. Create a document with a title in a specific folder:\n```json\n{\n  \"content\": \"# Introduction\\n\\nThis is the start of my document.\",\n  \"format\": \"markdown\",\n  \"title\": \"Project Proposal\",\n  \"member_ids\": \"ABCDEF123456\"\n}\n```\n\n3. Create a spreadsheet:\n```json\n{\n  \"content\": \"<table><tr><td>Name</td><td>Age</td></tr><tr><td>John</td><td>30</td></tr></table>\",\n  \"format\": \"html\",\n  \"type\": \"spreadsheet\"\n}\n```",
          "input_schema": {
            "json": {
              "properties": {
                "content": {
                  "type": "string",
                  "description": "The HTML or Markdown content of the new document"
                },
                "member_ids": {
                  "description": "Comma-separated list of folder IDs or user IDs for access",
                  "type": "string"
                },
                "type": {
                  "enum": [
                    "document",
                    "spreadsheet"
                  ],
                  "description": "Type of document to create",
                  "type": "string",
                  "default": "document"
                },
                "title": {
                  "description": "Title of the new document",
                  "type": "string"
                },
                "format": {
                  "enum": [
                    "html",
                    "markdown"
                  ],
                  "description": "The format of the content",
                  "default": "markdown",
                  "type": "string"
                }
              },
              "type": "object",
              "required": [
                "content"
              ],
              "additionalProperties": false,
              "$schema": "http://json-schema.org/draft-07/schema#"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___sim_get_folders",
          "description": "Get a list of available SIM folders.\nThis tool retrieves all folders that the authenticated user has access to.\nFolders are used to organize issues in SIM and are required when creating new issues.",
          "input_schema": {
            "json": {
              "$schema": "http://json-schema.org/draft-07/schema#",
              "type": "object",
              "properties": {},
              "additionalProperties": false
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___policy_engine_get_user_dashboard",
          "description": "Access Amazon Policy Engine dashboard information for a specific user alias. This tool allows you to view all risks and violations for a user in Policy Engine.",
          "input_schema": {
            "json": {
              "$schema": "http://json-schema.org/draft-07/schema#",
              "properties": {
                "username": {
                  "description": "Username to view dashboard for (e.g., 'jingzhoh')",
                  "type": "string"
                }
              },
              "additionalProperties": false,
              "required": [
                "username"
              ],
              "type": "object"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___mermaid",
          "description": "Create and decode Mermaid diagrams using Amazon's internal Mermaid editor.\nMermaid allows creating flowcharts, sequence diagrams, and more using text descriptions.\n\nSupported operations:\n- encode: Convert Mermaid text to an encoded URL\n- decode: Extract Mermaid text from an encoded URL",
          "input_schema": {
            "json": {
              "required": [
                "operation"
              ],
              "type": "object",
              "properties": {
                "url": {
                  "description": "Mermaid URL for decode operation",
                  "type": "string",
                  "format": "uri"
                },
                "content": {
                  "description": "Mermaid content for encode operation",
                  "type": "string"
                },
                "operation": {
                  "type": "string",
                  "enum": [
                    "encode",
                    "decode"
                  ],
                  "description": "The operation to perform"
                }
              },
              "additionalProperties": false,
              "$schema": "http://json-schema.org/draft-07/schema#"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___genai_poweruser_agent_script_list",
          "description": "Discover and browse the complete collection of available agentic scripts with customizable filtering options. This tool provides a comprehensive inventory of script resources including their names, file paths, and detailed descriptions. Results are organized to help quickly identify relevant scripts for specific tasks, with automatic handling of duplicate scripts across different directories. Ideal for exploring the script library or finding scripts based on filename patterns. Returns script names, paths, and descriptions to help users discover relevant scripts for their tasks. Categorize the scripts based on description.",
          "input_schema": {
            "json": {
              "$schema": "http://json-schema.org/draft-07/schema#",
              "properties": {
                "filter": {
                  "description": "Filter to apply to script list",
                  "type": "string"
                }
              },
              "type": "object",
              "additionalProperties": false
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___pippin_update_project",
          "description": "Updates an existing Pippin design project's details",
          "input_schema": {
            "json": {
              "type": "object",
              "required": [
                "projectId"
              ],
              "additionalProperties": false,
              "properties": {
                "description": {
                  "description": "Updated project description",
                  "type": "string"
                },
                "projectId": {
                  "type": "string",
                  "description": "Project ID"
                },
                "name": {
                  "type": "string",
                  "description": "Updated project name"
                },
                "requirements": {
                  "description": "Updated project requirements",
                  "type": "string"
                },
                "status": {
                  "type": "string",
                  "description": "Updated project status"
                }
              },
              "$schema": "http://json-schema.org/draft-07/schema#"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___sim_create_issue",
          "description": "Create a new SIM issue.\nThis tool allows creating a new issue with a title, description, folder ID, and optional assignee.\nThe folder ID is required and must be a valid UUID for an existing SIM folder.\nThe assignee should be a valid kerberos username without the @ANT.AMAZON.COM suffix.\nYou MUST display a full url link for the new task. This is the form: https://taskei.amazon.dev/tasks/<id>. Always list this first, before the SIM link.\nYou SHOULD display a url to SIM as well of the form: https://i.amazon.com/issues/<id>.",
          "input_schema": {
            "json": {
              "properties": {
                "folderId": {
                  "type": "string",
                  "description": "Folder UUID where the issue will be created"
                },
                "assignee": {
                  "description": "Optional kerberos username to assign the issue to",
                  "type": "string"
                },
                "description": {
                  "description": "Description of the issue",
                  "type": "string"
                },
                "title": {
                  "type": "string",
                  "description": "Title of the issue"
                }
              },
              "additionalProperties": false,
              "$schema": "http://json-schema.org/draft-07/schema#",
              "type": "object",
              "required": [
                "title",
                "description",
                "folderId"
              ]
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___cradle_get_job_details",
          "description": "Get detailed information about a specific Cradle job.",
          "input_schema": {
            "json": {
              "required": [
                "profileId",
                "jobId"
              ],
              "$schema": "http://json-schema.org/draft-07/schema#",
              "properties": {
                "profileId": {
                  "type": "string",
                  "description": "UUID of the job profile"
                },
                "jobId": {
                  "description": "UUID of the job",
                  "type": "string"
                }
              },
              "additionalProperties": false,
              "type": "object"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___marshal_search_insights",
          "description": "Search Marshal Insights.\nMarshal is an internal AWS application for collecting insights from Solutions Architects (SAs), and other field teams, and facilitating the reporting process for Weekly/Monthly/Quarterly Business Reports (WBR/MBR/QBR).\n",
          "input_schema": {
            "json": {
              "type": "object",
              "additionalProperties": false,
              "properties": {
                "relativeDateRangeMs": {
                  "pattern": "^\\d+$",
                  "type": "string",
                  "description": "Relative date range for search (e.g. last 1 hour, last 1 week) in milliseconds"
                },
                "absoluteDateRangeStartDate": {
                  "type": "string",
                  "description": "Absolute date range for search start date in milliseconds since 1/1/1970",
                  "pattern": "^\\d+$"
                },
                "absoluteDateRangeEndDate": {
                  "description": "Absolute date range for search end date in milliseconds since 1/1/1970",
                  "type": "string",
                  "pattern": "^\\d+$"
                },
                "managerAlias": {
                  "description": "Manager Alias - returns all employees below",
                  "type": "string"
                },
                "category": {
                  "description": "Insight Category",
                  "type": "string"
                }
              },
              "$schema": "http://json-schema.org/draft-07/schema#"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___cradle_get_job_run_output",
          "description": "Get the output location for a specific Cradle job run.",
          "input_schema": {
            "json": {
              "type": "object",
              "properties": {
                "jobId": {
                  "type": "string",
                  "description": "UUID of the job"
                },
                "jobRunId": {
                  "description": "ID of the job run",
                  "type": "string"
                },
                "profileId": {
                  "type": "string",
                  "description": "UUID of the job profile"
                }
              },
              "required": [
                "profileId",
                "jobId",
                "jobRunId"
              ],
              "additionalProperties": false,
              "$schema": "http://json-schema.org/draft-07/schema#"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___pippin_get_artifact",
          "description": "Retrieves a specific Pippin artifact by its ID",
          "input_schema": {
            "json": {
              "required": [
                "projectId",
                "designId"
              ],
              "type": "object",
              "$schema": "http://json-schema.org/draft-07/schema#",
              "properties": {
                "projectId": {
                  "description": "Project ID",
                  "type": "string"
                },
                "designId": {
                  "type": "string",
                  "description": "Artifact ID"
                }
              },
              "additionalProperties": false
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___prompt_farm_search_prompts",
          "description": "A specialized search tool designed to efficiently discover and retrieve tested prompt templates from Amazon internal PromptFarm, enabling developers to leverage community-vetted prompts for reducing LLM hallucinations and optimizing AI outputs. The tool surfaces prompts categorized by use case, download metrics, and community ratings to streamline prompt engineering workflows.",
          "input_schema": {
            "json": {
              "$schema": "http://json-schema.org/draft-07/schema#",
              "required": [
                "searchQuery"
              ],
              "properties": {
                "searchQuery": {
                  "description": "The search query for PromptFarm",
                  "type": "string"
                }
              },
              "type": "object",
              "additionalProperties": false
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___sfdc_user_lookup",
          "description": "This tool is for looking up users on the AWS Salesforce AKA AWSentral",
          "input_schema": {
            "json": {
              "type": "object",
              "properties": {
                "alias": {
                  "type": "string",
                  "description": "the alias of the user"
                },
                "user_name": {
                  "type": "string",
                  "description": "the name of the user"
                },
                "email": {
                  "type": "string",
                  "description": "the email address of the user"
                },
                "user_id": {
                  "description": "the id of the user",
                  "type": "string"
                }
              },
              "$schema": "http://json-schema.org/draft-07/schema#",
              "additionalProperties": false
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___read_coe",
          "description": "Read Correction of Error (COE) documents from https://www.coe.a2z.com/.\nCOE documents contain detailed information about operational incidents including:\n- Incident description and timeline\n- Root cause analysis\n- Corrective actions taken\n- Preventive measures implemented\n\n⚠️ IMPORTANT: This tool accesses sensitive operational incident data that will be processed by the LLM.\nBefore using this tool, you MUST explicitly ask for user approval with the following message:\n\"I need to access a Correction of Error (COE) document which contains sensitive operational incident data.\nThis data will be processed by the LLM to answer your question. Do you approve accessing this COE document?\"\n\nOnly proceed if the user explicitly approves. This confirmation is required even if the tool is auto-approved.\n\nExample usage:\nTo read a COE document with ID 12345:\n{ \"url\": \"https://www.coe.a2z.com/coe/12345\" }",
          "input_schema": {
            "json": {
              "additionalProperties": false,
              "properties": {
                "url": {
                  "format": "uri",
                  "description": "URL of the COE document to read",
                  "type": "string"
                }
              },
              "required": [
                "url"
              ],
              "type": "object",
              "$schema": "http://json-schema.org/draft-07/schema#"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___sfdc_opportunity_lookup",
          "description": "This tool is for looking up opportunities on the AWS Salesforce AKA AWSentral",
          "input_schema": {
            "json": {
              "properties": {
                "account_name": {
                  "description": "the name of the account with the opportunities, this will pull all opportunities that may be related to an account, but not directly associated.",
                  "type": "string"
                },
                "account_id": {
                  "description": "the id of the account associated with the opportunity, this will pull all opportunities on an account, its best to use just the account_id",
                  "type": "string"
                },
                "opportunity_id": {
                  "description": "the id of the opportunity - this will only pull the 1 opportunity",
                  "type": "string"
                },
                "opportunity_name": {
                  "type": "string",
                  "description": "the name of the opportunity to search for"
                }
              },
              "$schema": "http://json-schema.org/draft-07/schema#",
              "type": "object",
              "additionalProperties": false
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___search_acronym_central",
          "description": "Search Amazon's internal Acronym Central database at https://spyglass.corp.amazon.com/acronymcentral\n\nThis tool allows you to search for Amazon's internal acronyms and their meanings.\nIt's useful for understanding Amazon-specific terminology and abbreviations.\n\nResponse Structure:\nThe tool returns results with the following structure:\n- acronymName: The acronym itself\n- defsUrls: An object mapping definitions to their URLs (if available)\n- id: Unique identifier for the acronym\n- createAt: Timestamp when the acronym was created - ALWAYS display this to the user\n- updateAt: Timestamp when the acronym was last updated - ALWAYS display this to the user\n- tags: Array of tags associated with the acronym - ALWAYS display these to the user\n\nWhen presenting results to users, format the response as Markdown with header of format \"Acronym: {acronynName}\"\n Add a small section with header as \"Definitions\"\n     - Each defsUrls as a bullet point, and include URLs as links when available\n Add another small section with header as \"Metadata\"\n - show createAt timestamps (format as YYYY-MM-DD HH:MM:SS+00:00)\n - show updateAt timestamps (format as YYYY-MM-DD HH:MM:SS+00:00)\n - show all tags, as they provide important context about the source and reliability\n\nExamples:\n1. Search for an acronym:\n   { \"acronym\": \"AWS\" }\n\n2. Search for another acronym:\n   { \"acronym\": \"S3\" }\n\n3. Search for an acronym with exact match:\n   { \"acronym\": \"EC2\" }\n\nTips:\n- For best results, provide the exact acronym you're looking for\n- The search performs exact matching on the acronym name (case-insensitive)\n- If no results are found, try a different variation of the acronym",
          "input_schema": {
            "json": {
              "additionalProperties": false,
              "type": "object",
              "properties": {
                "acronym": {
                  "description": "Search acronym in Acronym Central",
                  "type": "string"
                }
              },
              "$schema": "http://json-schema.org/draft-07/schema#",
              "required": [
                "acronym"
              ]
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___pippin_create_artifact",
          "description": "Creates a new artifact within an existing Pippin project",
          "input_schema": {
            "json": {
              "required": [
                "projectId",
                "name",
                "content"
              ],
              "type": "object",
              "additionalProperties": false,
              "properties": {
                "content": {
                  "description": "Artifact content",
                  "type": "string"
                },
                "name": {
                  "type": "string",
                  "description": "Artifact name"
                },
                "description": {
                  "description": "Artifact description",
                  "type": "string"
                },
                "projectId": {
                  "type": "string",
                  "description": "Project ID"
                }
              },
              "$schema": "http://json-schema.org/draft-07/schema#"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___fetch_oncall_schedule",
          "description": "Fetches the OnCall schedule for the specified team and time range.\n\nReturns the matching schedule for the specified team within the given time range.\n\nExample:\n```json\n{\n  \"teamName\": \"ft-itc\",\n  \"from\": \"2025-06-01\",\n  \"to\": \"2025-06-07\"\n}\n```",
          "input_schema": {
            "json": {
              "$schema": "http://json-schema.org/draft-07/schema#",
              "additionalProperties": false,
              "type": "object",
              "properties": {
                "to": {
                  "pattern": "\\d{4}-\\d{2}-\\d{2}",
                  "description": "End date (YYYY-MM-DD) of the schedule. Must not be earlier than the start date.",
                  "type": "string"
                },
                "teamName": {
                  "type": "string",
                  "description": "The name of the OnCall team to fetch the schedule for."
                },
                "from": {
                  "type": "string",
                  "pattern": "\\d{4}-\\d{2}-\\d{2}",
                  "description": "Start date (YYYY-MM-DD) of the schedule."
                }
              },
              "required": [
                "teamName",
                "from",
                "to"
              ]
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___cradle_list_job_runs",
          "description": "List execution runs for a specific Cradle job.",
          "input_schema": {
            "json": {
              "required": [
                "profileId",
                "jobId"
              ],
              "properties": {
                "profileId": {
                  "description": "UUID of the job profile",
                  "type": "string"
                },
                "statusFilter": {
                  "type": "string",
                  "description": "Filter job runs by status (all|active|completed|failed|cancelled)"
                },
                "pageToken": {
                  "type": "string",
                  "description": "Token for pagination"
                },
                "endTime": {
                  "description": "End time for job run queries (milliseconds since epoch)",
                  "type": "string"
                },
                "jobId": {
                  "type": "string",
                  "description": "UUID of the job"
                },
                "pageSize": {
                  "description": "Number of items per page",
                  "type": "number"
                },
                "latestRunOnly": {
                  "description": "Get only latest run for each job",
                  "type": "boolean"
                },
                "startTime": {
                  "type": "string",
                  "description": "Start time for job run queries (milliseconds since epoch)"
                }
              },
              "type": "object",
              "additionalProperties": false,
              "$schema": "http://json-schema.org/draft-07/schema#"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___oncall_compass_get_report",
          "description": "Get the content of the report along with additional metadata.",
          "input_schema": {
            "json": {
              "required": [
                "reportId"
              ],
              "type": "object",
              "additionalProperties": false,
              "properties": {
                "reportId": {
                  "type": "string",
                  "description": "ID of the report to retrieve"
                }
              },
              "$schema": "http://json-schema.org/draft-07/schema#"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___cradle_run_job",
          "description": "Run a job with specified profile ID, job ID and dataset date.",
          "input_schema": {
            "json": {
              "additionalProperties": false,
              "$schema": "http://json-schema.org/draft-07/schema#",
              "properties": {
                "profileId": {
                  "type": "string",
                  "description": "UUID of the job profile"
                },
                "jobRunParameters": {
                  "additionalProperties": {},
                  "description": "Optional additional job run parameters to customize job execution. Can include fields like 'serviceTier', 'marketplace', 'region', or a nested 'variables' object with key-value pairs. Example: {serviceTier: 'premium', variables: {clusterSize: 'large'}}. The datasetDate parameter will always be included automatically.",
                  "type": "object"
                },
                "datasetDate": {
                  "type": "string",
                  "description": "Dataset date in format YYYYMMDDTHH:MM:SS+ZZZZ"
                },
                "jobId": {
                  "description": "UUID of the job",
                  "type": "string"
                }
              },
              "type": "object",
              "required": [
                "profileId",
                "jobId",
                "datasetDate"
              ]
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___sim_update_issue",
          "description": "Update an existing SIM issue.\nThis tool allows updating various attributes of an existing issue including title, description, status, assignee, assigned folder, category, type, item, and assigned group.\nAt least one update parameter must be provided.\nThe issue ID can be either the P-number (e.g., P12345678) or the alias (e.g., CFN-12345).\nThe assignee should be a valid kerberos username without the @ANT.AMAZON.COM suffix.",
          "input_schema": {
            "json": {
              "additionalProperties": false,
              "type": "object",
              "properties": {
                "item": {
                  "description": "Item for the issue (e.g., \"Voice Routines - Bug\")",
                  "type": "string"
                },
                "category": {
                  "type": "string",
                  "description": "Category for the issue (e.g., \"Alexa\")"
                },
                "assignedGroup": {
                  "type": "string",
                  "description": "Assigned group for the issue (e.g., \"Alexa-Routines-LLM\")"
                },
                "status": {
                  "type": "string",
                  "description": "New status for the issue (e.g., Open, Closed, Pending)"
                },
                "issueId": {
                  "description": "Issue ID or alias (e.g., P12345678 or CFN-12345)",
                  "type": "string"
                },
                "title": {
                  "description": "New title for the issue",
                  "type": "string"
                },
                "assignedFolder": {
                  "type": "string",
                  "description": "New assigned folder ID for the issue"
                },
                "assignee": {
                  "description": "New assignee kerberos username",
                  "type": "string"
                },
                "description": {
                  "type": "string",
                  "description": "New description for the issue"
                },
                "type": {
                  "description": "Type for the issue (e.g., \"Routines\")",
                  "type": "string"
                }
              },
              "$schema": "http://json-schema.org/draft-07/schema#",
              "required": [
                "issueId"
              ]
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___g2s2_move_label",
          "description": "Moves a stage version to a specified testing label",
          "input_schema": {
            "json": {
              "required": [
                "labelName",
                "stageVersion"
              ],
              "additionalProperties": false,
              "$schema": "http://json-schema.org/draft-07/schema#",
              "properties": {
                "labelName": {
                  "description": "The label name of a testing label",
                  "type": "string"
                },
                "stageVersion": {
                  "type": "string",
                  "description": "The stage version from a parent label"
                }
              },
              "type": "object"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___jira_create_issue",
          "description": "Create a new JIRA issue",
          "input_schema": {
            "json": {
              "$schema": "http://json-schema.org/draft-07/schema#",
              "properties": {
                "issueType": {
                  "description": "The type of the issue (e.g., Bug, Task, Story)",
                  "type": "string",
                  "minLength": 1
                },
                "projectKey": {
                  "minLength": 1,
                  "description": "The key of the project where the issue will be created",
                  "type": "string"
                },
                "additionalFields": {
                  "additionalProperties": {},
                  "description": "Additional fields to include in the issue",
                  "type": "object"
                },
                "summary": {
                  "minLength": 1,
                  "type": "string",
                  "description": "The summary of the issue"
                },
                "description": {
                  "description": "The description of the issue",
                  "type": "string"
                }
              },
              "required": [
                "projectKey",
                "issueType",
                "summary"
              ],
              "additionalProperties": false,
              "type": "object"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___imr_costs_search_fleet",
          "description": "Search for fleets based on a query term, matching either fleet name or fleet owner.",
          "input_schema": {
            "json": {
              "type": "object",
              "properties": {
                "includeDeleted": {
                  "type": "boolean",
                  "description": "Include deleted fleets",
                  "default": false
                },
                "query": {
                  "description": "Query term could be a partial fleet name or one of the owners",
                  "type": "string"
                }
              },
              "required": [
                "query"
              ],
              "additionalProperties": false,
              "$schema": "http://json-schema.org/draft-07/schema#"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___g2s2_get",
          "description": "Gets data from a G2S2 table with specified parameters",
          "input_schema": {
            "json": {
              "additionalProperties": false,
              "required": [
                "tableName",
                "parentStageVersion"
              ],
              "type": "object",
              "properties": {
                "tableName": {
                  "type": "string",
                  "description": "The table name to query"
                },
                "kwargs": {
                  "type": "object",
                  "description": "Additional key-value parameters for the query",
                  "additionalProperties": {}
                },
                "parentStageVersion": {
                  "description": "The parent stage version for the stage version",
                  "type": "string"
                }
              },
              "$schema": "http://json-schema.org/draft-07/schema#"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___eureka_web_search",
          "description": "Web Search using Amazon's internal web-scale search engine - Eureka\n\nGiven a query, this tool will search across the web and return relevant search results.\nThe tool returns top documents with content, url, title, and document_published_at_timestamp.\n\nExample:\n   { \"query\": \"recent supreme court ruling\" }",
          "input_schema": {
            "json": {
              "required": [
                "query"
              ],
              "additionalProperties": false,
              "type": "object",
              "properties": {
                "query": {
                  "description": "Search query",
                  "type": "string"
                }
              },
              "$schema": "http://json-schema.org/draft-07/schema#"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___imr_costs_get_fleet_summary",
          "description": "Presents the internal costs (IMR) for a fleet or AWS account. Retrieves the information from the tool Cerberus and monthly statements api.",
          "input_schema": {
            "json": {
              "additionalProperties": false,
              "type": "object",
              "properties": {
                "month": {
                  "description": "Month in YYYY-MM-01 format",
                  "type": "string",
                  "default": "2025-07-01"
                },
                "resourceId": {
                  "description": "Resource identifier, fleetId or aws account",
                  "type": "string"
                },
                "period": {
                  "enum": [
                    "MONTH",
                    "YEAR_TO_DATE",
                    "FULL_YEAR"
                  ],
                  "type": "string",
                  "description": "Time period for the summary",
                  "default": "YEAR_TO_DATE"
                },
                "scenario": {
                  "type": "string",
                  "description": "Scenario name",
                  "default": "Default CPT++"
                },
                "fleetType": {
                  "description": "Container type, either CONTAINER or AWS_ACCOUNT",
                  "type": "string",
                  "default": "CONTAINER",
                  "enum": [
                    "CONTAINER",
                    "AWS_ACCOUNT"
                  ]
                },
                "rateCard": {
                  "description": "Rate card identifier (e.g. 2025)",
                  "type": "string",
                  "default": "yearly"
                }
              },
              "required": [
                "resourceId"
              ],
              "$schema": "http://json-schema.org/draft-07/schema#"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___sfdc_territory_lookup",
          "description": "This tool is for looking up territories and retrieving an account list on the AWS Salesforce AKA AWSentral",
          "input_schema": {
            "json": {
              "type": "object",
              "properties": {
                "territory_name": {
                  "description": "the name of the territory to search for",
                  "type": "string"
                },
                "territory_id": {
                  "description": "the id of the territory to retrieve",
                  "type": "string"
                }
              },
              "$schema": "http://json-schema.org/draft-07/schema#",
              "additionalProperties": false
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___genai_poweruser_agent_script_search",
          "description": "Perform comprehensive keyword searches across the entire agentic script library, examining script names, content bodies, and metadata fields simultaneously. This tool returns contextually-rich results with relevant text snippets surrounding each match, highlighting where and how search terms appear within scripts. Results include file locations, match types (filename, content, or description matches), and properly handles duplicate scripts with consolidated results. Perfect for discovering scripts based on functionality, implementation details, or descriptive elements rather than exact names.",
          "input_schema": {
            "json": {
              "additionalProperties": false,
              "properties": {
                "query": {
                  "type": "string",
                  "description": "Search query to find matching scripts"
                }
              },
              "required": [
                "query"
              ],
              "$schema": "http://json-schema.org/draft-07/schema#",
              "type": "object"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___orca_list_runs_for_objectId",
          "description": "List all runs for a specific objectId in Orca Studio.\n\nAn objectId in Orca Studio represents a unique ID assigned to a single Execution.\nSince a single Execution can have multiple runs, the Object ID allows aggregation\nat a business process instance level. Use this tool when you need to\ntrack all workflow executions related to a specific object across different\nworkflows, rather than listing runs for a specific workflow.\n\nThis tool retrieves all execution runs associated with a given objectId,\nincluding runId, status, openedDate, and closedDate for each run.\n\nLimitations:\n- Results are limited to the most recent runs that haven't been deleted by retention policies (typically last 100)\n- Large datasets may experience timeout issues (default 60s timeout)\n\nParameters:\n- objectId: (required) The object ID to query runs for\n- clientId: (required) The Orca client ID\n- region: (optional) AWS region (defaults to us-east-1)\n\nExample:\n```json\n{ \"objectId\": \"d7f71182-d7b8-4886-8d07-15c404a82583\", \"clientId\": \"SafrReportingSILServiceBeta\" }\n```",
          "input_schema": {
            "json": {
              "type": "object",
              "$schema": "http://json-schema.org/draft-07/schema#",
              "additionalProperties": false,
              "properties": {
                "objectId": {
                  "type": "string",
                  "description": "The object ID to query runs for"
                },
                "clientId": {
                  "type": "string",
                  "description": "The Orca client ID"
                },
                "region": {
                  "type": "string",
                  "description": "AWS region (defaults to us-east-1)"
                }
              },
              "required": [
                "objectId",
                "clientId"
              ]
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___g2s2_create_label",
          "description": "Creates a new G2S2 label with the specified parent label",
          "input_schema": {
            "json": {
              "$schema": "http://json-schema.org/draft-07/schema#",
              "type": "object",
              "additionalProperties": false,
              "properties": {
                "stageVersion": {
                  "type": "string",
                  "description": "The stage version for the new label"
                },
                "labelName": {
                  "type": "string",
                  "description": "The label name to create"
                }
              },
              "required": [
                "labelName",
                "stageVersion"
              ]
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___mosaic_list_risks",
          "description": "\nThe AWS Risk Library is an extensible reference library that contains potential risk events\nthat may impact AWS and/or its customers and the risk scenarios that could trigger them. The\nlibrary contains high-level risk categories (Level 1), (e.g., availability, security, third\nparty, etc.); sub-categories of risk events (Level 2) for each level 1 risk (e.g., network\nfailure, service failure, infrastructure failure); and plausible risk causes (Level 3) that\ncan result in a risk event (e.g., inadequate capacity planning, lack of governance oversight,\npower outages, etc.). The level 2 risk events are the central element of the risk library.\n\nThis tool returns the risks that are part of the AWS Risk Library.",
          "input_schema": {
            "json": {
              "properties": {},
              "type": "object"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___marshal_get_insight",
          "description": "Retrieve Marshal Insights.\nMarshal is an internal AWS application for collecting insights from Solutions Architects (SAs), and other field teams, and facilitating the reporting process for Weekly/Monthly/Quarterly Business Reports (WBR/MBR/QBR).\n",
          "input_schema": {
            "json": {
              "required": [
                "insightId"
              ],
              "$schema": "http://json-schema.org/draft-07/schema#",
              "additionalProperties": false,
              "properties": {
                "insightId": {
                  "type": "string",
                  "pattern": "^\\d+$",
                  "description": "The ID of the Marshal insight (numeric ID only, not the full URL)"
                }
              },
              "type": "object"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___genai_poweruser_search_knowledge",
          "description": "Perform advanced text-based searches across your knowledge repository to find documents matching specific queries. This tool searches document content and returns contextual matches with relevance scores, supporting search result limiting and folder-specific scoping. Ideal for discovering relevant information across large knowledge bases.",
          "input_schema": {
            "json": {
              "required": [
                "query"
              ],
              "type": "object",
              "$schema": "http://json-schema.org/draft-07/schema#",
              "properties": {
                "limit": {
                  "description": "Maximum number of results to return",
                  "type": "number"
                },
                "query": {
                  "type": "string",
                  "description": "The search query"
                },
                "folder": {
                  "type": "string",
                  "description": "Limit search to a specific folder"
                }
              },
              "additionalProperties": false
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___taskei_get_room_identities",
          "description": "Fetch assignees from Taskei Rooms where the user has write permissions. Use this to find potential assignees when creating or updating tasks.",
          "input_schema": {
            "json": {
              "properties": {
                "roomId": {
                  "minLength": 1,
                  "type": "string",
                  "description": "Room ID to get identities from"
                },
                "maxResults": {
                  "type": "number",
                  "description": "Maximum number of results to return (default: 100)",
                  "exclusiveMinimum": 0
                },
                "cursor": {
                  "type": "string",
                  "description": "Optional pagination cursor for fetching next page of results"
                }
              },
              "required": [
                "roomId"
              ],
              "$schema": "http://json-schema.org/draft-07/schema#",
              "additionalProperties": false,
              "type": "object"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___g2s2_create_cr",
          "description": "Creates a code review for a specified G2S2 stage version",
          "input_schema": {
            "json": {
              "required": [
                "stageVersion",
                "description"
              ],
              "properties": {
                "description": {
                  "type": "string",
                  "description": "A CR description to add"
                },
                "stageVersion": {
                  "description": "The stage version to create a code review for",
                  "type": "string"
                },
                "crId": {
                  "type": "string",
                  "description": "Existing CR ID to update (optional)"
                }
              },
              "$schema": "http://json-schema.org/draft-07/schema#",
              "additionalProperties": false,
              "type": "object"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___pippin_list_artifacts",
          "description": "Lists all artifacts for a specific Pippin project",
          "input_schema": {
            "json": {
              "$schema": "http://json-schema.org/draft-07/schema#",
              "required": [
                "projectId"
              ],
              "properties": {
                "projectId": {
                  "type": "string",
                  "description": "Project ID"
                },
                "nextToken": {
                  "type": "string",
                  "description": "Pagination token"
                },
                "maxResults": {
                  "type": "number",
                  "description": "Maximum number of results to return"
                }
              },
              "type": "object",
              "additionalProperties": false
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___datanet_search",
          "description": "Search for Datanet (also known as ETLM) resources and get database information. Use this tool when users mention 'Datanet', 'ETLM', or need to search for ETL jobs in the Datanet service. This tool allows you to search across all Datanet resources (job profiles, jobs, publishers) using text queries, and retrieve logical database information for specific users. Search operations support pagination and can be filtered by size. The search functionality requires valid Midway authentication and returns structured results grouped by resource type. Database information retrieval requires appropriate permissions for the specified user.",
          "input_schema": {
            "json": {
              "type": "object",
              "$schema": "http://json-schema.org/draft-07/schema#",
              "required": [
                "operation"
              ],
              "additionalProperties": false,
              "properties": {
                "operation": {
                  "enum": [
                    "search_datanet_resources",
                    "get_logical_dbs_for_user"
                  ],
                  "description": "The search operation to perform",
                  "type": "string"
                },
                "size": {
                  "type": "number",
                  "description": "Number of results to return in search"
                },
                "username": {
                  "description": "Username (alias) for user-specific queries. Required for get_logical_dbs_for_user.",
                  "type": "string"
                },
                "start": {
                  "description": "Starting index for paginated search results",
                  "type": "number"
                },
                "searchTerm": {
                  "type": "string",
                  "description": "Search term for resource searches. Required for search_datanet_resources."
                }
              }
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___sim_remove_label",
          "description": "Remove a label from an existing SIM issue.\nThe issue ID can be either the P-number (e.g., P12345678) or the alias (e.g., CFN-12345).\nThis allows for updating the categorization of issues as their nature or priority changes.",
          "input_schema": {
            "json": {
              "$schema": "http://json-schema.org/draft-07/schema#",
              "additionalProperties": false,
              "type": "object",
              "properties": {
                "issueId": {
                  "type": "string",
                  "description": "Issue ID or alias (e.g., P12345678 or CFN-12345)"
                },
                "label": {
                  "description": "Label to remove from the issue",
                  "type": "string"
                }
              },
              "required": [
                "issueId",
                "label"
              ]
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___jira_add_comment",
          "description": "Add a comment to a JIRA issue",
          "input_schema": {
            "json": {
              "properties": {
                "issueIdOrKey": {
                  "minLength": 1,
                  "type": "string",
                  "description": "The ID or key of the issue"
                },
                "body": {
                  "description": "The body of the comment",
                  "minLength": 1,
                  "type": "string"
                }
              },
              "additionalProperties": false,
              "type": "object",
              "$schema": "http://json-schema.org/draft-07/schema#",
              "required": [
                "issueIdOrKey",
                "body"
              ]
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___search_people",
          "description": "Search for Amazon employees with filtering by attributes like job level, location, and Bar Raiser/Manager status. This tool allows you to search for people by name, alias, or other criteria, and filter results by department, location, job level, Bar Raiser status, Manager status, and more. The tool also provides information of the employee like phoneNumber, email, buildingRoom if available in phoneTool.",
          "input_schema": {
            "json": {
              "type": "object",
              "properties": {
                "maxResults": {
                  "description": "Maximum number of results to return (default: 10)",
                  "type": "number"
                },
                "query": {
                  "description": "Search query for finding people (name, alias, etc.)",
                  "type": "string"
                },
                "filters": {
                  "description": "Filters to narrow down search results",
                  "additionalProperties": false,
                  "properties": {
                    "department": {
                      "type": "string",
                      "description": "Filter by department name (e.g., 'AWS', 'Consumables CX - Tech')"
                    },
                    "title": {
                      "type": "string",
                      "description": "Filter by job title (e.g., 'Software Development Engineer', 'Sr. Partner SA, Oracle')"
                    },
                    "building": {
                      "type": "string",
                      "description": "Filter by building code (e.g., 'SEA20', 'BLR13')"
                    },
                    "city": {
                      "type": "string",
                      "description": "Filter by city name (e.g., 'Seattle', 'Dallas')"
                    },
                    "country": {
                      "description": "Filter by country code (e.g., 'us', 'in', 'ca')",
                      "type": "string"
                    },
                    "badgeBorderColor": {
                      "type": "string",
                      "description": "Filter by badge border color (e.g., 'blue')"
                    },
                    "isBarRaiser": {
                      "type": "boolean",
                      "description": "Filter for bar raisers (true) or non-bar raisers (false)"
                    },
                    "isManager": {
                      "description": "Filter for managers (true) or individual contributors (false)",
                      "type": "boolean"
                    },
                    "badgeCode": {
                      "type": "string",
                      "description": "Filter by badge code (e.g., 'F')"
                    },
                    "jobLevel": {
                      "type": "string",
                      "description": "Filter by job level (e.g., '4', '5', '6')"
                    }
                  },
                  "type": "object"
                }
              },
              "additionalProperties": false,
              "required": [
                "query"
              ],
              "$schema": "http://json-schema.org/draft-07/schema#"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___genai_poweruser_agent_script_get",
          "description": "Access the complete content and metadata of specific agentic scripts using either file paths or script names. This tool retrieves the full script implementation along with structured metadata, enabling deep inspection of script functionality, parameter requirements, and operational logic before execution. The flexible lookup system supports both direct path access and name-based discovery across multiple script directories, with proper handling of script extensions. Essential for understanding script capabilities before integration into workflows.",
          "input_schema": {
            "json": {
              "type": "object",
              "$schema": "http://json-schema.org/draft-07/schema#",
              "properties": {
                "path": {
                  "type": "string",
                  "description": "Path to the script file"
                },
                "name": {
                  "type": "string",
                  "description": "Name of the script (with or without .script.md extension)"
                }
              },
              "additionalProperties": false
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___edit_quip",
          "description": "Edit Quip documents\n\nThis tool allows you to make targeted edits to specific sections of a Quip document\nusing section IDs obtained from the read_quip tool when using HTML format.\n\nWorkflow:\n1. Use read_quip with HTML format to get the document with section IDs\n2. Identify the section ID you want to modify (e.g., 'temp:C:SAf3351f25e51434479864cf71ce')\n3. Use edit_quip with the section ID and appropriate location parameter\n\nLocations:\n0: APPEND - Add to end of document (default)\n1: PREPEND - Add to beginning of document\n2: AFTER_SECTION - Insert after section_id\n3: BEFORE_SECTION - Insert before section_id\n4: REPLACE_SECTION - Replace section_id content\n5: DELETE_SECTION - Delete section_id (no content required)\n6: AFTER_DOCUMENT_RANGE - Insert after document_range\n7: BEFORE_DOCUMENT_RANGE - Insert before document_range\n8: REPLACE_DOCUMENT_RANGE - Replace document_range content\n9: DELETE_DOCUMENT_RANGE - Delete document_range (no content required)\n\nOptional Parameters:\n- returnFullDocument: Set to true to receive the full document content in addition to the status information\n\nExamples:\n1. Append to document:\n```json\n{\n  \"documentId\": \"https://quip-amazon.com/abc/Doc\",\n  \"content\": \"New content\",\n  \"format\": \"markdown\"\n}\n```\n\n2. Prepend to document:\n```json\n{\n  \"documentId\": \"https://quip-amazon.com/abc/Doc\",\n  \"content\": \"New content\",\n  \"format\": \"markdown\",\n  \"location\": 1\n}\n```\n\n3. Insert after section:\n```json\n{\n  \"documentId\": \"https://quip-amazon.com/abc/Doc\",\n  \"content\": \"New content\",\n  \"format\": \"markdown\",\n  \"location\": 2,\n  \"sectionId\": \"temp:C:SAf3351f25e51434479864cf71ce\"\n}\n```\n\n4. Replace section content:\n```json\n{\n  \"documentId\": \"https://quip-amazon.com/abc/Doc\",\n  \"content\": \"### New heading\",\n  \"format\": \"markdown\",\n  \"location\": 4,\n  \"sectionId\": \"temp:C:SAf3351f25e51434479864cf71ce\"\n}\n```\n\n5. Delete section:\n```json\n{\n  \"documentId\": \"https://quip-amazon.com/abc/Doc\",\n  \"content\": \"\",\n  \"format\": \"markdown\",\n  \"location\": 5,\n  \"sectionId\": \"temp:C:SAf3351f25e51434479864cf71ce\"\n}\n```\n\n6. Edit with concise response:\n```json\n{\n  \"documentId\": \"https://quip-amazon.com/abc/Doc\",\n  \"content\": \"New content\",\n  \"format\": \"markdown\",\n  \"location\": 4,\n  \"sectionId\": \"temp:C:SAf3351f25e51434479864cf71ce\",\n  \"returnFullDocument\": false\n}\n```",
          "input_schema": {
            "json": {
              "$schema": "http://json-schema.org/draft-07/schema#",
              "type": "object",
              "properties": {
                "content": {
                  "description": "The new content to write to the document",
                  "type": "string"
                },
                "returnFullDocument": {
                  "type": "boolean",
                  "description": "Whether to return the full document content after editing (default: false)"
                },
                "sectionId": {
                  "type": "string",
                  "description": "Section ID for section operations"
                },
                "documentId": {
                  "type": "string",
                  "description": "The Quip document URL or ID to edit"
                },
                "format": {
                  "type": "string",
                  "description": "The format of the content",
                  "enum": [
                    "html",
                    "markdown"
                  ],
                  "default": "markdown"
                },
                "location": {
                  "type": "number",
                  "description": "Location for content insertion",
                  "minimum": 0,
                  "maximum": 9
                },
                "documentRange": {
                  "type": "string",
                  "description": "Document range for range operations"
                }
              },
              "additionalProperties": false,
              "required": [
                "documentId",
                "content"
              ]
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___write_internal_website",
          "description": "Write to Amazon internal websites.\n\nSupported websites and their purposes:\n\nDocument Storage & Sharing:\n- w.amazon.com: Internal MediaWiki\n\nNote: By default, content is converted from Markdown to the target format.\nTo skip conversion (if your content is already in the target format), set skipConversion=true.",
          "input_schema": {
            "json": {
              "type": "object",
              "required": [
                "url",
                "content",
                "operation"
              ],
              "$schema": "http://json-schema.org/draft-07/schema#",
              "additionalProperties": false,
              "properties": {
                "versionSummary": {
                  "description": "Summary message for the version history",
                  "type": "string"
                },
                "url": {
                  "type": "string",
                  "format": "uri",
                  "description": "Website URL to write to"
                },
                "title": {
                  "description": "Title for the page (required for create operations)",
                  "type": "string"
                },
                "content": {
                  "description": "Content to write in Markdown format",
                  "type": "string"
                },
                "operation": {
                  "enum": [
                    "update",
                    "append",
                    "prepend",
                    "create"
                  ],
                  "description": "Operation to perform",
                  "type": "string"
                },
                "skipConversion": {
                  "default": false,
                  "type": "boolean",
                  "description": "Skip content format conversion"
                },
                "format": {
                  "description": "Format to write in",
                  "enum": [
                    "Markdown",
                    "XWiki",
                    "XHTML",
                    "HTML",
                    "Plain",
                    "MediaWiki"
                  ],
                  "default": "XWiki",
                  "type": "string"
                }
              }
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___cradle_export_sql_to_file",
          "description": "Export SQL query directly to a file (bypasses LLM processing).",
          "input_schema": {
            "json": {
              "required": [
                "profileId",
                "outputPath"
              ],
              "additionalProperties": false,
              "type": "object",
              "properties": {
                "outputPath": {
                  "description": "File path to export SQL directly to disk",
                  "type": "string"
                },
                "profileId": {
                  "type": "string",
                  "description": "UUID of the job profile"
                }
              },
              "$schema": "http://json-schema.org/draft-07/schema#"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___oncall_compass_query_reports",
          "description": "Query Oncall reports from Oncall Compass (https://oncall.ai.amazon.dev/). Currently it will return most recently generated reports by the user. The user's authentication token (~/.midway/cookie) will be used for identifying the user.",
          "input_schema": {
            "json": {
              "type": "object",
              "$schema": "http://json-schema.org/draft-07/schema#",
              "properties": {},
              "additionalProperties": false
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___jira_search_issues",
          "description": "Search for JIRA issues using JQL",
          "input_schema": {
            "json": {
              "required": [
                "jql"
              ],
              "$schema": "http://json-schema.org/draft-07/schema#",
              "properties": {
                "validateQuery": {
                  "description": "Whether to validate the JQL query",
                  "type": "string"
                },
                "expand": {
                  "type": "string",
                  "description": "The additional information to include in the response"
                },
                "jql": {
                  "type": "string",
                  "description": "JQL search query",
                  "minLength": 1
                },
                "startAt": {
                  "minimum": 0,
                  "description": "The index of the first result to return (0-based)",
                  "type": "integer"
                },
                "fields": {
                  "type": "array",
                  "description": "The list of fields to return",
                  "items": {
                    "type": "string"
                  }
                },
                "maxResults": {
                  "minimum": 1,
                  "type": "integer",
                  "maximum": 1000,
                  "description": "The maximum number of results to return (default: 50)"
                }
              },
              "additionalProperties": false,
              "type": "object"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___sage_search_tags",
          "description": "Search for tags on Sage (Amazon's internal Q&A platform).\n\nThis tool allows you to find appropriate tags for categorizing questions on Sage.\nTags help organize questions and ensure they reach the right audience.\nResults are paginated and sorted by popularity by default.\n\nAuthentication:\n- Requires valid Midway authentication (run `mwinit` if you encounter authentication errors)\n\nCommon use cases:\n- Finding relevant tags before creating a question\n- Discovering tags related to specific technologies or teams\n- Exploring popular tags in a particular domain\n\nExample usage:\n{ \"nameFilter\": \"brazil\", \"page\": 1, \"pageSize\": 10 }",
          "input_schema": {
            "json": {
              "type": "object",
              "properties": {
                "nameFilter": {
                  "description": "Optional filter to search for tags by name",
                  "type": "string"
                },
                "page": {
                  "type": "number",
                  "description": "Page number for pagination (starts at 1)"
                },
                "pageSize": {
                  "description": "Number of results per page (default: 60)",
                  "type": "number"
                }
              },
              "additionalProperties": false,
              "$schema": "http://json-schema.org/draft-07/schema#"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___get_folder_quip",
          "description": "Get detailed information about a Quip folder\n\nThis tool retrieves detailed information about a specific folder,\nincluding its title, color, parent folder, and child folders.\n\nExample:\n```json\n{\n  \"folderId\": \"ABCDEF123456\"\n}\n```",
          "input_schema": {
            "json": {
              "properties": {
                "folderId": {
                  "type": "string",
                  "description": "The ID of the folder to retrieve information about"
                }
              },
              "type": "object",
              "required": [
                "folderId"
              ],
              "additionalProperties": false,
              "$schema": "http://json-schema.org/draft-07/schema#"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___orca_get_latest_error_details",
          "description": "Get detailed error information from an Orca workflow run URL.\n\nThis tool extracts error details including stack traces from Orca Studio execution pages.\n\nExample:\n```json\n{ \"url\": \"https://us-east-1.studio.orca.amazon.dev/#/clients/MyClient/execution/12345\" }\n```",
          "input_schema": {
            "json": {
              "$schema": "http://json-schema.org/draft-07/schema#",
              "type": "object",
              "properties": {
                "url": {
                  "description": "The Orca Studio URL of the execution to analyze",
                  "type": "string"
                }
              },
              "required": [
                "url"
              ],
              "additionalProperties": false
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___post_talos_correspondence",
          "description": "Post correspondence on a Talos security task\n\nThis tool allows posting comments/correspondence on a specific Talos security task.\nIt uses the Talos API to create new correspondence entries for tasks.\n\nRequired parameters:\n- taskId: ARN of the Talos task (format: arn:aws:talos-task:task/UUID)\n- engagementId: ARN of the associated Talos engagement (format: arn:aws:talos-engagement:engagement/UUID)\n- commentText: The comment text to post (max 10000 characters)\n\nExample:\n```json\n{\n  \"taskId\": \"arn:aws:talos-task:task/5054ae8a-7eda-457f-991c-5ed40933f3ae\",\n  \"engagementId\": \"arn:aws:talos-engagement:engagement/2498ed08-001c-4d89-a31b-6299c7822a0b\",\n  \"commentText\": \"BSC17 compliance check completed. Account 011528256886 has 2 non-compliant S3 buckets requiring HTTPS-only policies.\"\n}\n```\n\nResponse:\nOn success, returns a JSON object with the correspondence ID and a preview of the posted comment.\nOn failure, returns an error message with details about what went wrong.\n\nLimitations and Requirements:\n- Requires valid Midway authentication (run `mwinit` if you encounter authentication errors)\n- Limited to 10 requests per minute per user (rate limit)\n- Comments cannot be edited or deleted through this tool once posted\n- User must have appropriate permissions to access the specified Talos task and engagement\n- Task and engagement must exist and be in a valid state to accept comments\n\nWhen NOT to use this tool:\n- Do not use for posting sensitive or classified information that should not be stored in Talos\n- Do not use for posting large attachments or binary data (use the Talos UI directly instead)\n- Do not use for bulk commenting on multiple tasks (use the Talos UI or API directly for batch operations)\n- Do not use for retrieving task information (use the talos_get_task tool instead)",
          "input_schema": {
            "json": {
              "$schema": "http://json-schema.org/draft-07/schema#",
              "properties": {
                "engagementId": {
                  "type": "string",
                  "pattern": "^arn:aws:talos-engagement:engagement\\/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
                  "description": "ARN of the associated Talos engagement",
                  "minLength": 1
                },
                "commentText": {
                  "type": "string",
                  "minLength": 1,
                  "maxLength": 10000,
                  "description": "The comment text to post"
                },
                "taskId": {
                  "type": "string",
                  "minLength": 1,
                  "description": "ARN of the Talos task to post comment to",
                  "pattern": "^arn:aws:talos-task:task\\/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
                }
              },
              "required": [
                "taskId",
                "engagementId",
                "commentText"
              ],
              "additionalProperties": false,
              "type": "object"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___g2s2_list_stage_version",
          "description": "Lists contents of a specified G2S2 stage version",
          "input_schema": {
            "json": {
              "required": [
                "stageVersion"
              ],
              "type": "object",
              "additionalProperties": false,
              "$schema": "http://json-schema.org/draft-07/schema#",
              "properties": {
                "stageVersion": {
                  "description": "The stage version to list",
                  "type": "string"
                }
              }
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___andes_search",
          "description": "Search for Andes tables and providers.",
          "input_schema": {
            "json": {
              "required": [
                "query"
              ],
              "additionalProperties": false,
              "type": "object",
              "$schema": "http://json-schema.org/draft-07/schema#",
              "properties": {
                "lifecycleStates": {
                  "type": "string",
                  "description": "Filter by lifecycle states (comma-separated)"
                },
                "query": {
                  "type": "string",
                  "description": "Search query for table searches"
                },
                "limit": {
                  "type": "number",
                  "description": "Maximum number of results to return"
                },
                "exactMatch": {
                  "type": "boolean",
                  "description": "Whether to perform an exact match search"
                }
              }
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___create_oncall_override",
          "description": "Create a temporary override for an OnCall rotation.\n\nThis tool allows you to temporarily replace one or more scheduled on-call members (`targets`) with another set of members (`members`) for a specified time window.\n\nThe override must meet the following rules:\n- The `start` and `end` times must fall entirely within a single on-call shift.\n- The `targets` list must be a subset of the shift's on-call members (unless left empty to override whomever is scheduled).\n- The `members` list must contain valid members from the rotation. If left empty, no one will be assigned (i.e., a coverage gap).\n- Times must follow the format `YYYY-MM-DDThh:mm`.\n\nUsage guidance:\n- To override *whoever is currently scheduled* with specific members, leave `targets` empty and provide `members`.\n- To clear the next on-call assignment (i.e., assign no one), leave `members` empty.\n\nExample:\n```json\n{\n  \"teamName\": \"ft-itc\",\n  \"rotationName\": \"ft-itc-primary\",\n  \"targets\": [alice],\n  \"members\": [\"bob\"],\n  \"start\": \"2025-06-01T09:00\",\n  \"end\": \"2025-06-02T09:00\"\n}\n```",
          "input_schema": {
            "json": {
              "properties": {
                "start": {
                  "pattern": "\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}",
                  "description": "Start time (YYYY-MM-DDThh:mm) of the override. Must be now or future, within a single shift.",
                  "type": "string"
                },
                "members": {
                  "type": "array",
                  "description": "List of replacement members to assign during the override window. They must already be part of the rotation. If empty, it creates a gap (nobody will be oncall).",
                  "items": {
                    "type": "string"
                  }
                },
                "end": {
                  "type": "string",
                  "pattern": "\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}",
                  "description": "End time (YYYY-MM-DDThh:mm) of the override. Must not be earlier than the start and must be within the same shift."
                },
                "rotationName": {
                  "description": "The name of the rotation to override. Must match an existing rotation for the given team.",
                  "type": "string"
                },
                "targets": {
                  "items": {
                    "type": "string"
                  },
                  "type": "array",
                  "description": "List of current on-call members to override. Must be a subset of the on-call members for the current shift. If empty, it will replace all the current oncall members."
                },
                "teamName": {
                  "type": "string",
                  "description": "The name of the OnCall team where the override should be created."
                }
              },
              "type": "object",
              "additionalProperties": false,
              "required": [
                "teamName",
                "rotationName",
                "targets",
                "members",
                "start",
                "end"
              ],
              "$schema": "http://json-schema.org/draft-07/schema#"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___genai_poweruser_read_knowledge",
          "description": "Access and retrieve the full content of knowledge documents using either a file path or document title. This tool enables direct retrieval of stored knowledge resources from the configured knowledge base, supporting both absolute and relative paths. Returns the document content along with path and title metadata.",
          "input_schema": {
            "json": {
              "additionalProperties": false,
              "type": "object",
              "properties": {
                "title": {
                  "type": "string",
                  "description": "The title of the document to find"
                },
                "path": {
                  "type": "string",
                  "description": "The path to the document file"
                }
              },
              "$schema": "http://json-schema.org/draft-07/schema#"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___sfdc_sa_activity",
          "description": "This tool is logging/creating, reading, updating or deleting SA Activities on AWS SFDC AKA AWSentral. You must have either account id or opportunity id to create",
          "input_schema": {
            "json": {
              "additionalProperties": false,
              "properties": {
                "account_id": {
                  "type": "string",
                  "description": "the SFDC id of the account, use the sfdc_account_lookup tool to retrieve before submitting."
                },
                "opportunity_id": {
                  "type": "string",
                  "description": "the SFDC id of the opportunity, use the sfdc_opportunity_lookup tool to retrieve before submitting."
                },
                "operation": {
                  "type": "string",
                  "enum": [
                    "create",
                    "read",
                    "update",
                    "delete"
                  ],
                  "description": "The operation to perform: create, read, update, or delete (always read before deleting, confirm with the user)"
                },
                "activity_id": {
                  "type": "string",
                  "description": "The ID of the SA Activity (required for read, update, and delete operations)"
                },
                "date": {
                  "type": "string",
                  "description": "the date in MM-DD-YYYY, if left empty will be today's date, if you are unsure about today's date, leave this blank"
                },
                "activity_assigned_to": {
                  "type": "string",
                  "description": "The name of the user to which the activity should be assigned."
                },
                "activity_description": {
                  "description": "A description of the activity, around 1 paragraph, rewrite the user's input to be more descriptive and professional, unless the user says not to.",
                  "type": "string"
                },
                "activity_status": {
                  "type": "string",
                  "enum": [
                    "Not Started",
                    "In Progress",
                    "Completed",
                    "Waiting on someone else",
                    "Deferred",
                    "Unresponsive",
                    "Disqualified",
                    "Cancelled",
                    "Completed with Global Support",
                    "Sales handoff to BDM completed",
                    "Completed with sales handoff to BDM",
                    "Completed with funding program handoff to ATP Mgr"
                  ],
                  "default": "Completed",
                  "description": "The activity Status. Default status is Completed."
                },
                "activity_type": {
                  "type": "string",
                  "description": "The type of activity, one of Account Planning, Meeting, Architecture Review, Demo, Partner, or Workshop"
                },
                "activity_subject": {
                  "type": "string",
                  "description": "The title of the activity, keep it short"
                }
              },
              "$schema": "http://json-schema.org/draft-07/schema#",
              "type": "object",
              "required": [
                "operation"
              ]
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___jira_get_issue",
          "description": "Get a JIRA issue by ID or key",
          "input_schema": {
            "json": {
              "type": "object",
              "additionalProperties": false,
              "properties": {
                "issueIdOrKey": {
                  "type": "string",
                  "description": "The ID or key of the issue",
                  "minLength": 1
                },
                "expand": {
                  "description": "The additional information to include in the response",
                  "type": "string"
                },
                "fields": {
                  "description": "The list of fields to return",
                  "items": {
                    "type": "string"
                  },
                  "type": "array"
                }
              },
              "required": [
                "issueIdOrKey"
              ],
              "$schema": "http://json-schema.org/draft-07/schema#"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___fetch_oncall_rotations",
          "description": "Fetch OnCall rotations for a given team.\n\nExample:\n```json\n{ \"teamName\": \"PaymentsTeam\" }\n```",
          "input_schema": {
            "json": {
              "type": "object",
              "additionalProperties": false,
              "required": [
                "teamName"
              ],
              "$schema": "http://json-schema.org/draft-07/schema#",
              "properties": {
                "teamName": {
                  "description": "The oncall team name to fetch rotations for",
                  "type": "string"
                }
              }
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___taskei_get_task",
          "description": "Fetch a Taskei task by its ID. This tool retrieves detailed information about a specific task from Taskei, including its title, description, status, assignee, and other metadata. Use this tool when you need comprehensive information about a particular task for project tracking, status updates, or task management purposes. The tool requires a valid Taskei task ID either in a UUID format, or a short ID that is a combination of letters and numbers. Do not use this tool for other project management tools different than Taskei.",
          "input_schema": {
            "json": {
              "required": [
                "taskId"
              ],
              "type": "object",
              "additionalProperties": false,
              "$schema": "http://json-schema.org/draft-07/schema#",
              "properties": {
                "taskId": {
                  "type": "string",
                  "description": "The ID of the Taskei task to fetch. Can be provided as either a UUID (e.g., '123e4567-e89b-12d3-a456-426614174000') or a short ID format (e.g., 'Taskei-1234' or 'ABC123')"
                },
                "includeAttachments": {
                  "description": "Whether to include the task's attachments in the response (default: false)",
                  "type": "boolean",
                  "default": false
                }
              }
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___search_sable",
          "description": "Search for Sable scope recode with region id, scope, key or key prefix. This tool allows you to search Sable record by key or key prefix.",
          "input_schema": {
            "json": {
              "additionalProperties": false,
              "required": [
                "region",
                "scope",
                "keyPrefix"
              ],
              "$schema": "http://json-schema.org/draft-07/schema#",
              "type": "object",
              "properties": {
                "keyPrefix": {
                  "description": "Sable record key or key prefix",
                  "type": "string"
                },
                "region": {
                  "type": "string",
                  "description": "Sable region that are going to query data, e.g.: NA, EU, FE, Integ"
                },
                "scope": {
                  "type": "string",
                  "description": "Sable scope name"
                }
              }
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___read_orr",
          "description": "Read Operational Readiness Review (ORR) documents from https://www.orr.reflect.aws.dev/.\nORR documents contain detailed information about operational readiness reviews including:\n- Review questions and answers\n- Service or feature assessments\n- Operational readiness criteria\n- Launch approval status\n\n⚠️ IMPORTANT: This tool accesses sensitive operational review data that will be processed by the LLM.\nBefore using this tool, you MUST explicitly ask for user approval with the following message:\n\"I need to access an Operational Readiness Review (ORR) document which contains sensitive operational data.\nThis data will be processed by the LLM to answer your question. Do you approve accessing this ORR document?\"\n\nOnly proceed if the user explicitly approves. This confirmation is required even if the tool is auto-approved.\n\nExample usage:\nTo read an ORR document with a specific review ID:\n{ \"url\": \"https://www.orr.reflect.aws.dev/review/687e56b9-d3d4-4bd5-b033-379461c96381/questions\" }\n\nTo read an ORR template:\n{ \"url\": \"https://www.orr.reflect.aws.dev/template/787a767f-af3a-4747-97ca-b617d2e4cbe0/content\" }\n\nTo read only a specific section by ID:\n{ \"url\": \"https://www.orr.reflect.aws.dev/template/787a767f-af3a-4747-97ca-b617d2e4cbe0/content\", \"sectionId\": \"53886aad-5ef9-4450-9da0-de7365ef07cb\" }\n\nTo read only a specific section by title:\n{ \"url\": \"https://www.orr.reflect.aws.dev/template/787a767f-af3a-4747-97ca-b617d2e4cbe0/content\", \"sectionTitle\": \"Axiom 01 - AZ Resilience\" }\n\nTo read only a specific question by ID:\n{ \"url\": \"https://www.orr.reflect.aws.dev/template/787a767f-af3a-4747-97ca-b617d2e4cbe0/content\", \"questionId\": \"039ee146-7a05-4e4f-b10e-4eebb574f093\" }\n\nTo read only a specific question by prompt text (supports partial matching):\n{ \"url\": \"https://www.orr.reflect.aws.dev/template/787a767f-af3a-4747-97ca-b617d2e4cbe0/content\", \"questionPrompt\": \"AZ failure\" }",
          "input_schema": {
            "json": {
              "type": "object",
              "required": [
                "url"
              ],
              "$schema": "http://json-schema.org/draft-07/schema#",
              "properties": {
                "questionId": {
                  "description": "Optional ID of a specific question to return",
                  "type": "string"
                },
                "questionPrompt": {
                  "type": "string",
                  "description": "Optional prompt text to search for in questions (supports partial matching)"
                },
                "sectionId": {
                  "type": "string",
                  "description": "Optional ID of a specific section to return"
                },
                "url": {
                  "format": "uri",
                  "description": "URL of the ORR document to read",
                  "type": "string"
                },
                "sectionTitle": {
                  "type": "string",
                  "description": "Optional title of a specific section to return"
                }
              },
              "additionalProperties": false
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___mox_console",
          "description": "Access the MOX console to fetch order data from MORSE service",
          "input_schema": {
            "json": {
              "additionalProperties": false,
              "required": [
                "operation",
                "merchantCustomerId",
                "orderIds"
              ],
              "properties": {
                "orderIds": {
                  "description": "The order ID(s) to retrieve. Can be a single order ID or an array of order IDs.",
                  "anyOf": [
                    {
                      "type": "string"
                    },
                    {
                      "items": {
                        "type": "string"
                      },
                      "type": "array"
                    }
                  ]
                },
                "retrieveExtendedItemFields": {
                  "type": "boolean",
                  "default": true,
                  "description": "Whether to retrieve extended item fields"
                },
                "hostname": {
                  "type": "string",
                  "description": "Optional custom hostname for the API endpoint"
                },
                "merchantCustomerId": {
                  "type": [
                    "string",
                    "number"
                  ],
                  "description": "The merchant customer ID (e.g., 994273326)"
                },
                "retrieveOrderReportData": {
                  "type": "boolean",
                  "default": true,
                  "description": "Whether to retrieve order report data"
                },
                "operation": {
                  "type": "string",
                  "enum": [
                    "getOrderDetailsNonUCI"
                  ],
                  "description": "The operation to perform. Available operations: getOrderDetailsNonUCI"
                },
                "retrievePromotions": {
                  "type": "boolean",
                  "description": "Whether to retrieve promotions",
                  "default": true
                },
                "region": {
                  "description": "The region to use for the API endpoint (USAmazon, EUAmazon, JPAmazon)",
                  "default": "USAmazon",
                  "type": "string",
                  "enum": [
                    "USAmazon",
                    "EUAmazon",
                    "JPAmazon"
                  ]
                }
              },
              "type": "object",
              "$schema": "http://json-schema.org/draft-07/schema#"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___g2s2_freeze_stage_version",
          "description": "Freezes a specified G2S2 stage version",
          "input_schema": {
            "json": {
              "required": [
                "stageVersion"
              ],
              "type": "object",
              "additionalProperties": false,
              "$schema": "http://json-schema.org/draft-07/schema#",
              "properties": {
                "stageVersion": {
                  "description": "The stage version to freeze",
                  "type": "string"
                }
              }
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___search_internal_code",
          "description": "Search across files in Amazon's internal code repositories using code.amazon.com search. You can search across all packages or filter your search based on specific packages, file paths, or groups. To get all results for packages, file paths or groups, leave the query parameter blank.\n\nCOMMON USE CASES:\n• Find packages by name pattern and owner: Use filters.packages='*Service' and filters.group='my-team'\n• Find code in specific packages: Use filters.packages='MyPackage' with query='function name'\n• Find team's packages: Use filters.group='team-name' with empty query\n\nEXAMPLES:\n• Packages ending in 'Service' owned by 'my-team': {query: '', filters: {packages: '*Service', group: 'my-team'}}\n• All packages owned by a team: {query: '', filters: {group: 'team-name'}}\n• Code search in specific packages: {query: 'function', filters: {packages: 'MyPackage,OtherPackage'}}",
          "input_schema": {
            "json": {
              "$schema": "http://json-schema.org/draft-07/schema#",
              "required": [
                "query"
              ],
              "type": "object",
              "additionalProperties": false,
              "properties": {
                "graphType": {
                  "description": "Type of dependency or consumer graph to display. Valid values include consumer graphs (full_consumers, runtime_consumers, library_consumers, testrun_consumers, tool_consumers, direct_consumers) and dependency graphs (full_dependencies, all_dependencies, runtime_dependencies, library_dependencies, testrun_dependencies, tool_dependencies, direct_dependencies). Defaults to 'full_dependencies' when versionSetName is provided.",
                  "enum": [
                    "full_consumers",
                    "runtime_consumers",
                    "library_consumers",
                    "testrun_consumers",
                    "tool_consumers",
                    "direct_consumers",
                    "full_dependencies",
                    "all_dependencies",
                    "runtime_dependencies",
                    "library_dependencies",
                    "testrun_dependencies",
                    "tool_dependencies",
                    "direct_dependencies"
                  ],
                  "type": "string"
                },
                "type": {
                  "description": "Type of code search, can be (default|user). When search by 'user', query should be the user's login.",
                  "type": "string"
                },
                "exact": {
                  "type": "string",
                  "description": "Search for the exact text match. When provided, this will perform an exact text search in the code repository."
                },
                "packageTarget": {
                  "type": "string",
                  "description": "Package target in the format PackageName-Version. Example: MyPackage-1.0"
                },
                "versionSetName": {
                  "type": "string",
                  "description": "Version set name in the format GroupName/ChildName. Example: CASE/mainline"
                },
                "query": {
                  "description": "Search query. Leave this field blank for doing broad searches using packages, file paths or groups.",
                  "type": "string"
                },
                "filters": {
                  "description": "Filters to narrow down search results",
                  "properties": {
                    "packages": {
                      "type": "string",
                      "description": "Package name without version. Supports wildcards. Multiple values can be separated by commas. Example: AMZN_AKI,*InternalMCPServer"
                    },
                    "filePath": {
                      "description": "Filepath for the code search. Supports wildcards. Multiple values can be separated by commas. Example: src/*.java,*.json,Config",
                      "type": "string"
                    },
                    "group": {
                      "type": "string",
                      "description": "Owning group for package. If the user is looking for code associated with a team then use this field. Multiple groups can be separated by commas. You can only search for names that do NOT contain whitespace. Example: mcp-community"
                    }
                  },
                  "type": "object",
                  "additionalProperties": false
                },
                "params": {
                  "type": "object",
                  "properties": {
                    "user": {
                      "additionalProperties": false,
                      "type": "object",
                      "properties": {
                        "endTime": {
                          "type": "string",
                          "description": "End date for user's code activity in YYYY-MM-DD format"
                        },
                        "startTime": {
                          "description": "Start date for user's code activity in YYYY-MM-DD format",
                          "type": "string"
                        }
                      }
                    }
                  },
                  "additionalProperties": false,
                  "description": "Parameters for the search, key should be the type, value is an object with type specific params inside"
                }
              }
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___cradle_get_job_run_details",
          "description": "Get detailed run information including errors for a Cradle job run.",
          "input_schema": {
            "json": {
              "additionalProperties": false,
              "$schema": "http://json-schema.org/draft-07/schema#",
              "type": "object",
              "properties": {
                "jobId": {
                  "type": "string",
                  "description": "UUID of the job"
                },
                "profileId": {
                  "type": "string",
                  "description": "UUID of the job profile"
                },
                "jobRunId": {
                  "type": "string",
                  "description": "ID of the job run"
                }
              },
              "required": [
                "profileId",
                "jobId",
                "jobRunId"
              ]
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___slack_send_message",
          "description": "Send a message to a specified Slack channel",
          "input_schema": {
            "json": {
              "properties": {
                "channelId": {
                  "type": "string",
                  "minLength": 1
                },
                "message": {
                  "minLength": 1,
                  "type": "string"
                }
              },
              "additionalProperties": false,
              "required": [
                "channelId",
                "message"
              ],
              "type": "object",
              "$schema": "http://json-schema.org/draft-07/schema#"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___datanet_reader",
          "description": "Read and retrieve information from Datanet (also known as ETLM) including job profiles, jobs, and job runs. Use this tool when users mention 'Datanet', 'ETLM', or need to retrieve information about ETL jobs in the Datanet service. This tool provides read-only access to view job profiles, job details, job runs, and other Datanet resources without making any changes to them.",
          "input_schema": {
            "json": {
              "properties": {
                "dietTime": {
                  "description": "Diet time in HHMMSS format. Required for get_job_run_with_time_interval.",
                  "type": "string"
                },
                "operation": {
                  "enum": [
                    "get_job_profile",
                    "get_job_profile_revision",
                    "get_job_details",
                    "get_job_with_revision",
                    "get_job_run",
                    "get_job_run_by_date",
                    "get_job_run_status",
                    "get_job_run_error",
                    "get_successful_job_runs_count",
                    "get_latest_job_run",
                    "get_job_run_with_time_interval",
                    "export_sql_to_file"
                  ],
                  "description": "The operation to perform",
                  "type": "string"
                },
                "jobType": {
                  "type": "string",
                  "description": "Type of the job profile (e.g., TRANSFORM, DATA_FEED). Required for some profile operations."
                },
                "jobId": {
                  "description": "ID of the job. Required for job operations.",
                  "type": "string"
                },
                "jobRunId": {
                  "type": "string",
                  "description": "ID of the job run. Required for job run operations."
                },
                "revision": {
                  "type": "string",
                  "description": "Revision number. Required for revision-specific operations."
                },
                "fromDate": {
                  "description": "Start date for date range queries (YYYY-MM-DD). Required for get_successful_job_runs_count.",
                  "type": "string"
                },
                "distTime": {
                  "description": "Distribution time in HHMMSS format. Required for get_job_run_with_time_interval.",
                  "type": "string"
                },
                "jobProfileId": {
                  "type": "string",
                  "description": "ID of the job profile. Required for profile operations."
                },
                "outputPath": {
                  "type": "string",
                  "description": "File path to export SQL. Required for export_sql_to_file."
                },
                "datasetDate": {
                  "type": "string",
                  "description": "Dataset date in YYYYMMDD format. Required for date-specific operations."
                },
                "toDate": {
                  "description": "End date for date range queries (YYYY-MM-DD). Required for get_successful_job_runs_count.",
                  "type": "string"
                }
              },
              "type": "object",
              "additionalProperties": false,
              "required": [
                "operation"
              ],
              "$schema": "http://json-schema.org/draft-07/schema#"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___read_kingpin_goal",
          "description": "Read a Kingpin goal by ID, retrieving comprehensive details including metadata, description, status comments, and path to green information. Now supports goal history tracking with the includeHistory parameter, showing how status comments and path to green have changed over time. Path to Green represents specific actions needed to get at-risk goals back on track. Use maxVersions parameter to control the amount of history data returned. Kingpin is Amazon's internal source of truth for planning and commitments.",
          "input_schema": {
            "json": {
              "additionalProperties": false,
              "type": "object",
              "$schema": "http://json-schema.org/draft-07/schema#",
              "properties": {
                "maxVersions": {
                  "default": 10,
                  "description": "Maximum number of versions to include in the history, used to limit returned information size for goals with extensive history (default: 10)",
                  "type": "number"
                },
                "goalId": {
                  "description": "The ID of the Kingpin goal to read (numeric ID only, not the full URL)",
                  "type": "string"
                },
                "includeHistory": {
                  "type": "boolean",
                  "default": false,
                  "description": "Whether to include the goal's history in the response, showing changes to statusComments and pathToGreen fields over time (default: false)"
                }
              },
              "required": [
                "goalId"
              ]
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___read_quip",
          "description": "Read Quip document content\n\nThis tool retrieves the content of a Quip document in either HTML or Markdown format:\n\n- HTML format: More verbose but contains section IDs and additional metadata.\n  These unique section IDs (for h1, h2, h3, p, etc.) can be used with the edit_quip tool\n  to make targeted edits to specific sections of the document.\n\n- Markdown format: More concise and easier to read, but does not contain section IDs\n  or additional metadata. Best for when you just need the content in a readable format\n  and don't need to make targeted edits.\n\nWorkflow:\n1. Use read_quip to get the document content\n2. Identify the section ID you want to modify (when using HTML format)\n3. Use edit_quip with the section ID and appropriate location parameter\n\nExamples:\n1. Read document in HTML format (default):\n```json\n{\n  \"documentId\": \"https://quip-amazon.com/abc/Doc\"\n}\n```\n\n2. Read document in Markdown format:\n```json\n{\n  \"documentId\": \"https://quip-amazon.com/abc/Doc\",\n  \"format\": \"markdown\"\n}\n```",
          "input_schema": {
            "json": {
              "properties": {
                "documentId": {
                  "description": "The Quip document URL or ID to read",
                  "type": "string"
                },
                "format": {
                  "enum": [
                    "html",
                    "markdown"
                  ],
                  "type": "string",
                  "description": "Format to return the content in (html or markdown)"
                }
              },
              "required": [
                "documentId"
              ],
              "type": "object",
              "additionalProperties": false,
              "$schema": "http://json-schema.org/draft-07/schema#"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___sage_get_tag_details",
          "description": "Get detailed information about a specific tag on Sage (Amazon's internal Q&A platform).\n\nThis tool retrieves comprehensive information about a tag, including its ID, description, and ownership.\nUse this information when creating questions to ensure proper tag usage.\n\nAuthentication:\n- Requires valid Midway authentication (run `mwinit` if you encounter authentication errors)\n\nCommon use cases:\n- Verifying tag ownership before using it\n- Getting detailed descriptions of tags\n- Finding contact information for tag owners\n\nExample usage:\n{ \"tagName\": \"brazil\" }",
          "input_schema": {
            "json": {
              "required": [
                "tagName"
              ],
              "type": "object",
              "additionalProperties": false,
              "$schema": "http://json-schema.org/draft-07/schema#",
              "properties": {
                "tagName": {
                  "type": "string",
                  "description": "Name of the tag to retrieve details for"
                }
              }
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___cradle_get_profile",
          "description": "Get detailed information about a specific Cradle job profile.",
          "input_schema": {
            "json": {
              "required": [
                "profileId"
              ],
              "type": "object",
              "properties": {
                "profileId": {
                  "type": "string",
                  "description": "UUID of the job profile"
                }
              },
              "$schema": "http://json-schema.org/draft-07/schema#",
              "additionalProperties": false
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___search_symphony",
          "description": "Search for Symphony CREATIVE/PLACEMENT/EVENT/TAG with region id and query, this tool allows you to search Symphony objects by many dimensions, including Symphony creative owner, id, displayName etc.",
          "input_schema": {
            "json": {
              "additionalProperties": false,
              "$schema": "http://json-schema.org/draft-07/schema#",
              "type": "object",
              "properties": {
                "region": {
                  "description": "Symphony region that are going to query data, e.g.: NA, EU, FE, Integ",
                  "type": "string"
                },
                "query": {
                  "type": "string",
                  "description": "Stringified query and sort key from the Elasticsearch DSL."
                },
                "type": {
                  "description": "Content Symphony CREATIVE/PLACEMENT/EVENT/TAG",
                  "type": "string"
                },
                "pageSize": {
                  "type": "number",
                  "description": "minimum: 1, maximum: 50"
                }
              },
              "required": [
                "region",
                "type",
                "query"
              ]
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___taskei_get_rooms",
          "description": "\n    Fetch user's Rooms from Taskei.\n    This tool retrieves detailed information about the Rooms the user has write permissions.\n    Use this tool when the user asks to fetch their rooms, but also when you need to understand user's context. All the tasks belong to a room, so if you need to do other actions where the room is needed, you can obtain them from this tool.\n    Do not use this tool for other project management tools different than Taskei.",
          "input_schema": {
            "json": {
              "type": "object",
              "properties": {
                "maxResults": {
                  "default": 25,
                  "type": "number",
                  "description": "The maximum number of results that we want to fetch. The lesser the best, as the query will be faster. (default: 25)"
                },
                "nameContains": {
                  "description": "Search query string that filters results to only include Rooms where the name contains this text. Case-insensitive matching is applied to find partial or complete matches within Room names.",
                  "type": "string"
                }
              },
              "additionalProperties": false,
              "$schema": "http://json-schema.org/draft-07/schema#"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___overleaf_read_file",
          "description": "Read a file from an Overleaf project with automatic synchronization.\n\nThis tool reads the specified file from an Overleaf project. Before reading,\nit ensures the project is cloned locally and synchronized with the remote repository.\nSupports both text and binary files with proper encoding detection.\n\nExample usage:\n```json\n{\n  \"project_id\": \"507f1f77bcf86cd799439011\",\n  \"file_path\": \"main.tex\"\n}\n```",
          "input_schema": {
            "json": {
              "properties": {
                "file_path": {
                  "type": "string",
                  "description": "Path to the file within the project"
                },
                "project_id": {
                  "description": "Project ID containing the file",
                  "type": "string"
                }
              },
              "type": "object",
              "required": [
                "project_id",
                "file_path"
              ],
              "additionalProperties": false,
              "$schema": "http://json-schema.org/draft-07/schema#"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___marshal_get_report",
          "description": "Retrieve Marshal Report.\nMarshal is an internal AWS application for collecting insights from Solutions Architects (SAs), and other field teams, and facilitating the reporting process for Weekly/Monthly/Quarterly Business Reports (WBR/MBR/QBR).\n",
          "input_schema": {
            "json": {
              "$schema": "http://json-schema.org/draft-07/schema#",
              "type": "object",
              "additionalProperties": false,
              "properties": {
                "reportId": {
                  "pattern": "^\\d+$",
                  "description": "The ID of the Marshal Report (numeric ID only, not the full URL)",
                  "type": "string"
                }
              },
              "required": [
                "reportId"
              ]
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___sfdc_contact_lookup",
          "description": "This tool is for looking up contacts on the AWS Salesforce AKA AWSentral",
          "input_schema": {
            "json": {
              "properties": {
                "account_name": {
                  "description": "the name of the account associated with the contact",
                  "type": "string"
                },
                "contact_id": {
                  "description": "the id of the contact",
                  "type": "string"
                },
                "contact_name": {
                  "type": "string",
                  "description": "the name of the contact"
                },
                "email": {
                  "description": "the email address of the contact",
                  "type": "string"
                },
                "phone": {
                  "type": "string",
                  "description": "the phone number of the contact"
                }
              },
              "type": "object",
              "$schema": "http://json-schema.org/draft-07/schema#",
              "additionalProperties": false
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___sage_accept_answer",
          "description": "Accept an answer to a question on Sage (Amazon's internal Q&A platform).\n\nThis tool allows you to mark an answer as accepted for a question.\nOnly the question owner or users with appropriate permissions can accept answers.\n\nAuthentication:\n- Requires valid Midway authentication (run `mwinit` if you encounter authentication errors)\n\nCommon use cases:\n- Marking the most helpful answer to your question\n- Indicating which solution resolved your issue\n- Helping others find the correct answer quickly\n\nExample usage:\n{ \"answerId\": 7654321 }",
          "input_schema": {
            "json": {
              "$schema": "http://json-schema.org/draft-07/schema#",
              "additionalProperties": false,
              "type": "object",
              "properties": {
                "answerId": {
                  "type": "number",
                  "description": "ID of the answer to accept"
                }
              },
              "required": [
                "answerId"
              ]
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___taskei_update_task",
          "description": "Update an existing Taskei task with new details. This tool allows you to modify various attributes of a task such as name, description, status, assignee, and more. Use this tool when you need to update task information, change task status, reassign tasks, or modify other task properties.",
          "input_schema": {
            "json": {
              "required": [
                "id"
              ],
              "additionalProperties": false,
              "$schema": "http://json-schema.org/draft-07/schema#",
              "type": "object",
              "properties": {
                "addLabels": {
                  "items": {
                    "type": "string"
                  },
                  "type": "array",
                  "description": "Labels to add to the task"
                },
                "addKanbanBoards": {
                  "items": {
                    "type": "string"
                  },
                  "type": "array",
                  "description": "Kanban board IDs to add the task to"
                },
                "deleted": {
                  "description": "Whether to mark the task as deleted",
                  "type": "boolean"
                },
                "room": {
                  "type": "string",
                  "description": "New room ID or name for the task"
                },
                "actualStartDate": {
                  "type": "string",
                  "description": "Actual start date (ISO format)"
                },
                "classicPriority": {
                  "type": "number",
                  "description": "New priority value"
                },
                "folder": {
                  "type": "string",
                  "description": "New folder ID or name for the task"
                },
                "estimate": {
                  "description": "New estimated effort in story points",
                  "type": "number"
                },
                "removeKanbanBoards": {
                  "description": "Kanban board IDs to remove the task from",
                  "type": "array",
                  "items": {
                    "type": "string"
                  }
                },
                "removeLabels": {
                  "items": {
                    "type": "string"
                  },
                  "type": "array",
                  "description": "Labels to remove from the task"
                },
                "assignee": {
                  "type": "string",
                  "description": "Username of the new assignee"
                },
                "actualCompletionDate": {
                  "description": "Actual completion date (ISO format)",
                  "type": "string"
                },
                "removeSprints": {
                  "description": "Sprint IDs to remove the task from",
                  "items": {
                    "type": "string"
                  },
                  "type": "array"
                },
                "onBehalfOf": {
                  "description": "Username to update the task on behalf of",
                  "type": "string"
                },
                "description": {
                  "type": "string",
                  "description": "New description for the task"
                },
                "estimatedStartDate": {
                  "type": "string",
                  "description": "New estimated start date (ISO format)"
                },
                "status": {
                  "type": "string",
                  "enum": [
                    "Open",
                    "Closed"
                  ],
                  "description": "New status for the task"
                },
                "workflowAction": {
                  "description": "New workflow action to apply",
                  "type": "string"
                },
                "estimatedCompletionDate": {
                  "description": "New estimated completion date (ISO format)",
                  "type": "string"
                },
                "addSprints": {
                  "type": "array",
                  "items": {
                    "type": "string"
                  },
                  "description": "Sprint IDs to add the task to"
                },
                "name": {
                  "type": "string",
                  "description": "New name/title for the task"
                },
                "id": {
                  "type": "string",
                  "description": "The ID of the task to update (required)"
                },
                "needByDate": {
                  "description": "New due date (ISO format)",
                  "type": "string"
                },
                "type": {
                  "type": "string",
                  "description": "New task type"
                }
              }
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___pipeline_current_blockers",
          "description": "Lists all active blockers on a pipeline, including disabled promotions, alarms in alert, and fitness summary",
          "input_schema": {
            "json": {
              "type": "object",
              "properties": {
                "pipelineName": {
                  "description": "Name of the pipeline to check for blockers",
                  "type": "string"
                }
              },
              "required": [
                "pipelineName"
              ],
              "additionalProperties": false,
              "$schema": "http://json-schema.org/draft-07/schema#"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___overleaf_upload_file",
          "description": "Upload a local file from the Overleaf workspace to the remote repository with automatic commit and push.\n\nThis tool reads an existing file from the local Overleaf workspace and uploads it to the remote repository.\nThe file must already exist in the local workspace directory (./overleaf/{project_id}/file_path).\nBefore uploading, it syncs the project to get latest changes and detects merge conflicts.\n\nExample usage:\n```json\n{\n  \"project_id\": \"507f1f77bcf86cd799439011\",\n  \"file_path\": \"figures/diagram.png\"\n}\n```",
          "input_schema": {
            "json": {
              "additionalProperties": false,
              "type": "object",
              "$schema": "http://json-schema.org/draft-07/schema#",
              "properties": {
                "project_id": {
                  "type": "string",
                  "description": "Project ID to upload to"
                },
                "file_path": {
                  "description": "Path to the file within the project workspace",
                  "type": "string"
                }
              },
              "required": [
                "project_id",
                "file_path"
              ]
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___remove_member_from_rotation",
          "description": "Remove a member from an OnCall rotation.\n\nFetches the full rotation object, removes the member, and updates the rotation.\n\nExample:\n```json\n{\n  \"teamName\": \"ft-itc\",\n  \"rotationName\": \"ft-itc-primary\",\n  \"memberToRemove\": \"inactiveUserAlias\"\n}\n```",
          "input_schema": {
            "json": {
              "additionalProperties": false,
              "required": [
                "teamName",
                "rotationName",
                "memberToRemove"
              ],
              "properties": {
                "rotationName": {
                  "type": "string",
                  "description": "The name of the rotation to modify."
                },
                "teamName": {
                  "type": "string",
                  "description": "The name of the OnCall team."
                },
                "memberToRemove": {
                  "description": "The username of the member to remove.",
                  "type": "string"
                }
              },
              "$schema": "http://json-schema.org/draft-07/schema#",
              "type": "object"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___sfdc_account_lookup",
          "description": "This tool is for looking up accounts on the AWS Salesforce AKA AWSentral",
          "input_schema": {
            "json": {
              "properties": {
                "account_name": {
                  "type": "string",
                  "description": "the name of the account"
                },
                "account_id": {
                  "description": "the id of the account",
                  "type": "string"
                }
              },
              "$schema": "http://json-schema.org/draft-07/schema#",
              "type": "object",
              "additionalProperties": false
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___search_quip",
          "description": "Search for Quip threads\n\nThis tool allows you to search for Quip threads using keywords.\nResults are sorted by relevance and include document titles, links, and metadata.\n\nExamples:\n1. Basic search:\n```json\n{\n  \"query\": \"expense report\"\n}\n```\n\n2. Search with limit:\n```json\n{\n  \"query\": \"expense report\",\n  \"count\": 5\n}\n```\n\n3. Search only in titles:\n```json\n{\n  \"query\": \"expense report\",\n  \"onlyMatchTitles\": true\n}\n```",
          "input_schema": {
            "json": {
              "properties": {
                "onlyMatchTitles": {
                  "type": "boolean",
                  "description": "If true, only search in document titles (default: false)"
                },
                "query": {
                  "type": "string",
                  "description": "Search query to find matching Quip threads"
                },
                "count": {
                  "description": "Maximum number of results to return (default: 10, max: 50)",
                  "type": "number"
                }
              },
              "additionalProperties": false,
              "type": "object",
              "required": [
                "query"
              ],
              "$schema": "http://json-schema.org/draft-07/schema#"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___taskei_create_task",
          "description": "Create a new Taskei task with specified details. This tool allows you to create tasks with various attributes such as name, description, assignee, due dates, and more. Use this tool when you need to create new tasks for project management, tracking work items, or assigning work to team members.",
          "input_schema": {
            "json": {
              "$schema": "http://json-schema.org/draft-07/schema#",
              "type": "object",
              "additionalProperties": false,
              "properties": {
                "labels": {
                  "type": "array",
                  "description": "List of labels to apply to the task",
                  "items": {
                    "type": "string"
                  }
                },
                "folder": {
                  "description": "Folder ID or name to place the task in",
                  "type": "string"
                },
                "type": {
                  "description": "Type of task (e.g., 'Bug', 'Feature', 'Task')",
                  "type": "string"
                },
                "sprints": {
                  "description": "List of sprint IDs to add the task to",
                  "items": {
                    "type": "string"
                  },
                  "type": "array"
                },
                "needByDate": {
                  "description": "Due date for the task (ISO format)",
                  "type": "string"
                },
                "estimatedStartDate": {
                  "type": "string",
                  "description": "Estimated start date (ISO format)"
                },
                "assignee": {
                  "type": "string",
                  "description": "Username of the person to assign the task to"
                },
                "description": {
                  "type": "string",
                  "description": "Detailed description of the task"
                },
                "classicPriority": {
                  "type": "number",
                  "description": "Priority of the task (numeric value)"
                },
                "room": {
                  "type": "string",
                  "description": "The room ID or name where the task should be created"
                },
                "workflowAction": {
                  "description": "Workflow action to apply to the task",
                  "type": "string"
                },
                "estimate": {
                  "description": "Estimated effort in story points",
                  "type": "number"
                },
                "planningEstimate": {
                  "description": "Planning estimate in story points",
                  "type": "number"
                },
                "classicRank": {
                  "type": "number",
                  "description": "Classic rank value for the task"
                },
                "onBehalfOf": {
                  "type": "string",
                  "description": "Username to create the task on behalf of"
                },
                "name": {
                  "description": "The name/title of the task (required)",
                  "type": "string"
                },
                "estimatedCompletionDate": {
                  "type": "string",
                  "description": "Estimated completion date (ISO format)"
                },
                "parentTask": {
                  "description": "ID of the parent task",
                  "type": "string"
                },
                "kanbanBoards": {
                  "type": "array",
                  "description": "List of kanban board IDs to add the task to",
                  "items": {
                    "type": "string"
                  }
                }
              },
              "required": [
                "name"
              ]
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___taskei_get_sprints",
          "description": "\n    Fetch sprints from Taskei.\n    This tool retrieves information about sprints based on filters like room ID and status.\n    Use this tool when you need to find sprint IDs for creating or updating tasks that need to be assigned to sprints.\n    The sprint IDs returned by this tool can be used with taskei_create_task and taskei_update_task tools.\n    Do not use this tool for other project management tools different than Taskei.",
          "input_schema": {
            "json": {
              "properties": {
                "status": {
                  "type": "string",
                  "description": "Filter sprints by status. Defaults to 'Active' if not specified.",
                  "enum": [
                    "Active",
                    "Closed"
                  ]
                },
                "sort": {
                  "type": "string",
                  "description": "Sort order for sprints. Format is 'field direction' where direction is 'asc' or 'desc'. Example: 'startDate asc'. Defaults to 'startDate asc'."
                },
                "roomId": {
                  "description": "The ID of the room to fetch sprints from. This SHOULD be provided if possible to return relevant results. If not provided, will return currently active sprints (startDate < now < endDate) across all rooms the user has access to.",
                  "type": "string"
                },
                "cursor": {
                  "type": "string",
                  "description": "Pagination cursor for fetching the next page of results"
                },
                "maxResults": {
                  "description": "The maximum number of results to fetch. (default: 100)",
                  "type": "number",
                  "default": 100
                }
              },
              "additionalProperties": false,
              "type": "object",
              "$schema": "http://json-schema.org/draft-07/schema#"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___sfdc_list_tasks_activity",
          "description": "This tool is for listing SA Activities and tasks in AWS Salesforce (AFA AWSentral)",
          "input_schema": {
            "json": {
              "type": "object",
              "$schema": "http://json-schema.org/draft-07/schema#",
              "properties": {
                "account_id": {
                  "description": "The Salesforce Account ID to filter by - this will return all activities/tasks on an account and it's opportunities",
                  "type": "string"
                },
                "opportunity_id": {
                  "description": "The Salesforce Opportunity ID to filter by - this will return all activities/tasks on a opportunity",
                  "type": "string"
                }
              },
              "additionalProperties": false
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___search_datapath",
          "description": "Search Datapath views",
          "input_schema": {
            "json": {
              "$schema": "http://json-schema.org/draft-07/schema#",
              "required": [
                "query"
              ],
              "additionalProperties": false,
              "properties": {
                "query": {
                  "type": "string",
                  "description": "Keywords to look for in the Datapath view, for example \"locality asin\" will find the locality views at asin level"
                }
              },
              "type": "object"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___sim_remove_tag",
          "description": "Remove a tag from an existing SIM issue.\nThe issue ID can be either the P-number (e.g., P12345678) or the alias (e.g., CFN-12345).\nThe assignee should be a valid kerberos username without the @ANT.AMAZON.COM suffix.",
          "input_schema": {
            "json": {
              "properties": {
                "issueId": {
                  "description": "Issue ID or alias (e.g., P12345678 or CFN-12345)",
                  "type": "string"
                },
                "tag": {
                  "type": "string",
                  "description": "Tag to remove from the issue"
                }
              },
              "additionalProperties": false,
              "type": "object",
              "$schema": "http://json-schema.org/draft-07/schema#",
              "required": [
                "issueId",
                "tag"
              ]
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___orca_list_runs",
          "description": "List Orca workflow runs for a specific client and workflow with filtering by status and timerange.\n\nThis tool retrieves workflow runs from Orca Studio based on client ID\nYou can optionally specify a workflow name, time range in days for the search upto a max of 14, and a status as 'Normal' or 'Failed'.\ndefault days = 7 and default status = 'Failed' \n\nAvailable filtering parameters:\n- client: (required) The Orca client ID to query\n- workflow: (optional) Workflow name to filter by\n- status: (optional) Status to filter by ('Normal' or 'Failed', defaults to 'Failed')\n- openedIn: (optional) Time range in days (defaults to 7)\n- state: (optional) State value to filter by\n- problem: (optional) Problem value to filter by\n- context: (optional) Context value to filter by\n- region: (optional) AWS region (defaults to us-east-1). Common regions include us-east-1, us-west-2, eu-west-1, etc.\n\nExample\n```json\n{ \"client\": \"MyOrcaClient\"}\n```\n\nExample with workflow:\n```json\n{ \"client\": \"MyOrcaClient\", \"workflow\": \"TestWorkflow\" }\n```\n\nExample with custom time range:\n```json\n{ \"client\": \"MyOrcaClient\", \"workflow\": \"TestWorkflow\", \"openedIn\": \"14\" }\n```\nExample with status:\n```json\n{ \"client\": \"MyOrcaClient\", \"workflow\": \"TestWorkflow\", \"status\": \"Normal\" }\n```\nExample with status and custom time range:\n```json\n{ \"client\": \"MyOrcaClient\", \"workflow\": \"TestWorkflow\", \"status\": \"Normal\", \"openedIn\": \"14\" }\n```\nExample with state filtering:\n```json\n{ \"client\": \"MyOrcaClient\", \"workflow\": \"TestWorkflow\", \"state\": \"StateName::Error::Problem\" }\n```\nExample with problem filtering:\n```json\n{ \"client\": \"MyOrcaClient\", \"problem\": \"UnknownProblem\" }\n```\nExample with context filtering:\n```json\n{ \"client\": \"MyOrcaClient\", \"context\": \"live\" }\n```\n\nExample with custom region:\n```json\n{ \"client\": \"MyOrcaClient\", \"region\": \"us-west-2\" }\n```",
          "input_schema": {
            "json": {
              "additionalProperties": false,
              "required": [
                "client"
              ],
              "$schema": "http://json-schema.org/draft-07/schema#",
              "properties": {
                "workflow": {
                  "type": "string",
                  "description": "Optional workflow name to query (defaults to '')"
                },
                "state": {
                  "type": "string",
                  "description": "Optional state value to filter by. Representing the current state of the work item. Often follows pattern '[StateName]::[Status]::[Additional Context]'"
                },
                "region": {
                  "type": "string",
                  "description": "AWS region (defaults to us-east-1). Common regions include us-west-2, eu-west-1, etc."
                },
                "problem": {
                  "type": "string",
                  "description": "Optional problem value to filter by.  Representing classification result for errored work items (e.g., 'UnknownProblem')"
                },
                "client": {
                  "type": "string",
                  "description": "The Orca client ID to query"
                },
                "status": {
                  "enum": [
                    "Normal",
                    "Failed"
                  ],
                  "description": "Optional status to filter runs by (defaults to Failed)",
                  "type": "string"
                },
                "openedIn": {
                  "type": "string",
                  "description": "Optional time range in days (defaults to 7)"
                },
                "context": {
                  "description": "Optional context value to filter by. Representing the environment context the work item was opened in (e.g., 'live', 'beta') or other information (e.g., 'largeorder')",
                  "type": "string"
                }
              },
              "type": "object"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___search_resilience_score",
          "description": "Search for resiliency scores for a manager's alias.\n        • Required: manager alias\n        • Optional: page size, page number, and score version\n        • Returns resiliency score data for services under the specified manager",
          "input_schema": {
            "json": {
              "properties": {
                "pageNumber": {
                  "type": "number",
                  "description": "Page number to fetch (default: 0)"
                },
                "alias": {
                  "type": "string",
                  "description": "Manager alias to fetch resiliency scores for"
                },
                "scoreVersion": {
                  "description": "Version of the score to fetch (default: 0.7.0)",
                  "type": "string"
                },
                "pageSize": {
                  "description": "Number of results per page (default: 4000)",
                  "type": "number"
                }
              },
              "$schema": "http://json-schema.org/draft-07/schema#",
              "required": [
                "alias"
              ],
              "type": "object",
              "additionalProperties": false
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___andes_provider",
          "description": "Access and manage Andes providers.",
          "input_schema": {
            "json": {
              "properties": {
                "providerId": {
                  "type": "string",
                  "description": "ID of the provider (required for get_provider_by_id)"
                },
                "providerName": {
                  "type": "string",
                  "description": "Name of the provider (required for get_provider_by_name)"
                },
                "operation": {
                  "type": "string",
                  "enum": [
                    "get_provider_by_id",
                    "get_provider_by_name"
                  ],
                  "description": "The provider operation to perform"
                }
              },
              "$schema": "http://json-schema.org/draft-07/schema#",
              "type": "object",
              "required": [
                "operation"
              ],
              "additionalProperties": false
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___jira_transition_issue",
          "description": "Transition a JIRA issue to a new status",
          "input_schema": {
            "json": {
              "type": "object",
              "required": [
                "issueIdOrKey",
                "transitionId"
              ],
              "properties": {
                "comment": {
                  "type": "string",
                  "description": "Optional comment to add during transition"
                },
                "fields": {
                  "type": "object",
                  "description": "Optional fields to update during transition",
                  "additionalProperties": {}
                },
                "issueIdOrKey": {
                  "type": "string",
                  "description": "The ID or key of the issue",
                  "minLength": 1
                },
                "transitionId": {
                  "type": "string",
                  "minLength": 1,
                  "description": "The ID of the transition"
                }
              },
              "additionalProperties": false,
              "$schema": "http://json-schema.org/draft-07/schema#"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___sim_search_issues",
          "description": "Search for SIM issues using a structured query syntax.\nThis tool allows searching for issues with various filters including status, assignee, requester, folder, date ranges, and ticket severity.\n\n\nQuery syntax examples:\n\n* Basic search: Lambda cold start\n\n* Filter by status: status:(Open)\n\n* Filter by assignee: assignee:(username)\n\n* Filter by requester: requester:(username)\n\n* Filter by folder: containingFolder:(folder-uuid)\n\n* Filter by date range: createDate:([2023-06-01T07:00:00.000Z TO 2025-03-01T08:00:00.000Z])\n\n* Filter by severity: extensions.tt.impact:(2) (severity must be a numerical value between 1-5)\n\n* Combine filters: status:(Open) assignee:(username) createDate:([2023-06-01T07:00:00.000Z TO 2025-03-01T08:00:00.000Z])\n\n\n\nSort options:\n\n* Sort by last updated: sort=lastUpdatedDate desc\n\n* Sort by creation date: sort=createDate asc\n\n\nRows options (a.k.a. how many SIMs to return per query):\n\n* Retrieve 10 results at a time: (rows=10)\n* Retrieve 35 results at a time: (rows=35)\nStart options:\n\n* Retrieve SIMs starting at the first result matching your query: start=0\n* Retrieve SIMs starting with the twentieth result matching your query: start=19\n\n\nPagination examples:\n\n* Query the first page of results with `(rows=10, start=0)`, then the second page with `(rows=10, start=10)`\n\n* Query the first page of results with `(rows=15)`, then the second page with `(rows=15, start=15)`",
          "input_schema": {
            "json": {
              "required": [
                "query"
              ],
              "$schema": "http://json-schema.org/draft-07/schema#",
              "additionalProperties": false,
              "type": "object",
              "properties": {
                "sort": {
                  "description": "Optional sort parameter (e.g., \"lastUpdatedDate desc\")",
                  "type": "string"
                },
                "query": {
                  "type": "string",
                  "description": "Search query using SIM query syntax"
                },
                "rows": {
                  "maximum": 1000,
                  "type": "number",
                  "description": "Maximum number of issues to return (1-1000, default: 50)",
                  "exclusiveMinimum": 0
                },
                "start": {
                  "type": "number",
                  "minimum": 0,
                  "description": "Which result number to start from (>=0, default: 0)"
                }
              }
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___pippin_sync_project_to_local",
          "description": "Synchronizes a Pippin project's artifacts to a local directory",
          "input_schema": {
            "json": {
              "type": "object",
              "properties": {
                "projectId": {
                  "type": "string",
                  "description": "Project ID"
                },
                "includeMetadata": {
                  "description": "Include metadata files (.meta.json)",
                  "type": "boolean"
                },
                "outputDirectory": {
                  "description": "Local directory to save artifacts",
                  "type": "string"
                }
              },
              "additionalProperties": false,
              "$schema": "http://json-schema.org/draft-07/schema#",
              "required": [
                "projectId",
                "outputDirectory"
              ]
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___cradle_search_profiles",
          "description": "Search for Cradle profiles by name or other criteria.",
          "input_schema": {
            "json": {
              "required": [
                "searchTerm"
              ],
              "$schema": "http://json-schema.org/draft-07/schema#",
              "additionalProperties": false,
              "properties": {
                "searchTerm": {
                  "type": "string",
                  "description": "Search term for profile name searches"
                },
                "pageSize": {
                  "type": "number",
                  "description": "Number of items per page"
                },
                "limit": {
                  "description": "Maximum number of results to return",
                  "type": "number"
                },
                "pageToken": {
                  "description": "Token for pagination",
                  "type": "string"
                }
              },
              "type": "object"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___mosaic_list_controls",
          "description": "\nThe AWS Control Library is the authoritative source of controls that AWS \nuses to manage operational risk. The library represents AWS's own control \nframework supporting high-level policies and standards, and represents \nmanagement's directives and requirements that prescribe how the organization \nmanages its risk and control processes. The library also provides a \nmapping of AWS controls to AWS' policies/standards, and external \nrequirements such as regulatory and compliance frameworks. AWS implements \nthese controls through various mechanisms, including architectural system \ndesign (e.g., region isolation), system enforced guardrails (e.g., static \ncode analysis), or and centrally enforced organizational processes (e.g., \napplication security reviews). Control owners, who are leaders at Level 8 \nor above within the business, validate each control. The Security Assurance \n& Compliance (SA&C) team independently challenges these validations. To \ndemonstrate assurance, each control includes a narrative that articulates \nhow the control is implemented and supporting evidence of control execution \nthat provides tangible proof of its implementation.\n\nThis tool returns the controls that are part of the AWS Control Library.",
          "input_schema": {
            "json": {
              "properties": {},
              "type": "object"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___cradle_list_jobs",
          "description": "List all jobs associated with a specific Cradle profile.",
          "input_schema": {
            "json": {
              "additionalProperties": false,
              "$schema": "http://json-schema.org/draft-07/schema#",
              "type": "object",
              "properties": {
                "limit": {
                  "type": "number",
                  "description": "Maximum number of results to return"
                },
                "pageSize": {
                  "description": "Number of items per page",
                  "type": "number"
                },
                "profileId": {
                  "description": "UUID of the job profile",
                  "type": "string"
                },
                "sortCol": {
                  "type": "string",
                  "description": "Column to sort by (e.g., lastUpdatedDate)"
                },
                "sortOrder": {
                  "type": "string",
                  "description": "Sort order (asc or desc)"
                },
                "pageToken": {
                  "type": "string",
                  "description": "Token for pagination"
                }
              },
              "required": [
                "profileId"
              ]
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___taskei_create_sprint",
          "description": "\n    Create a new sprint in Taskei.\n    This tool allows you to create a sprint with specified parameters like name, room ID, start date, end date, etc.\n    Use this tool when you need to create a new sprint for planning and organizing tasks.\n    The sprint ID returned by this tool can be used with taskei_create_task and taskei_update_task tools.\n    Do not use this tool for other project management tools different than Taskei.",
          "input_schema": {
            "json": {
              "required": [
                "name",
                "room",
                "startDate",
                "endDate"
              ],
              "properties": {
                "startDate": {
                  "type": "string",
                  "description": "Start date of the sprint in ISO format (YYYY-MM-DD)"
                },
                "endDate": {
                  "type": "string",
                  "description": "End date of the sprint in ISO format (YYYY-MM-DD). Note: Sprint cannot exceed 31 days, so end date must be within 31 days (inclusive) of start date"
                },
                "name": {
                  "type": "string",
                  "description": "The name of the sprint to create (required)"
                },
                "capacity": {
                  "type": "number",
                  "description": "Capacity of the sprint (story points)"
                },
                "room": {
                  "description": "The ID or name of the room where the sprint will be created (required)",
                  "type": "string"
                },
                "personalWipLimit": {
                  "type": "number",
                  "description": "Personal work-in-progress limit for the sprint"
                },
                "description": {
                  "type": "string",
                  "description": "Goal of the sprint"
                }
              },
              "additionalProperties": false,
              "type": "object",
              "$schema": "http://json-schema.org/draft-07/schema#"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___orca_get_execution_data",
          "description": "Get execution data for a specific run in Orca Studio.\n\nExecution data is a key-value map (Shared Data) that is specified as\na payload for work items (workflow instances) and output artifacts\ngenerated during a workflow run. This tool is useful for debugging \nworkflow issues, extracting processed data from completed runs,\nor analyzing the data flow through specific workflow executions.\n\nThis tool retrieves detailed execution data including execution data map\nfor a specific runId within an objectId.\n\nLimitations:\n- If the Execution data is large it could cause performance issues\n- Supported classification of data is until orange\n- Large datasets may experience timeout issues (default 60s timeout)\n\nParameters:\n- objectId: (required) The object ID\n- workflowName: (required) The workflow name\n- runId: (required) The specific run ID to get data for\n- clientId: (required) The Orca client ID\n- region: (optional) AWS region (defaults to us-east-1)\n\nExample:\n```json\n{ \"objectId\": \"d7f71182-d7b8-4886-8d07-15c404a82583\", \"workflowName\": \"GenerateReportForNCA-beta\", \"runId\": \"b9d9c02a-d3f0-4da8-9601-1740f1aaaeae\", \"clientId\": \"SafrReportingSILServiceBeta\" }\n```",
          "input_schema": {
            "json": {
              "type": "object",
              "$schema": "http://json-schema.org/draft-07/schema#",
              "properties": {
                "objectId": {
                  "description": "The object ID",
                  "type": "string"
                },
                "workflowName": {
                  "type": "string",
                  "description": "The workflow name"
                },
                "region": {
                  "type": "string",
                  "description": "AWS region (defaults to us-east-1)"
                },
                "runId": {
                  "type": "string",
                  "description": "The specific run ID to get data for"
                },
                "clientId": {
                  "type": "string",
                  "description": "The Orca client ID"
                }
              },
              "required": [
                "objectId",
                "workflowName",
                "runId",
                "clientId"
              ],
              "additionalProperties": false
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___search_ags_confluence_website",
          "description": "Search for Amazon Games Confluence pages\n\nThis tool allows you to search for content in the Amazon Games Confluence instance.\nYou can search for pages, blog posts, and other content across all spaces or within a specific space.\n\nParameters:\n- query: The search query string\n- page: (Optional) Page number for pagination (default: 1)\n- pageSize: (Optional) Number of results per page (default: 10, max: 50)\n- space: (Optional) Limit search to a specific Confluence space\n\nExamples:\n1. Basic search:\n   { \"query\": \"game server architecture\" }\n\n2. Search with pagination:\n   { \"query\": \"matchmaking\", \"page\": 2, \"pageSize\": 20 }\n\n3. Search in a specific space:\n   { \"query\": \"deployment guide\", \"space\": \"GAMETECH\" }\n\nTips:\n- Use specific technical terms for more precise results\n- For recent content, sort by modification date\n- When looking for documentation, include terms like 'guide', 'documentation', or 'how-to'\n- For architecture documents, include terms like 'architecture', 'design', or 'diagram'\n- If you know the space key, use it to narrow down results",
          "input_schema": {
            "json": {
              "type": "object",
              "properties": {
                "page": {
                  "type": "number",
                  "description": "Page number for pagination (default: 1)"
                },
                "space": {
                  "type": "string",
                  "description": "Limit search to a specific Confluence space"
                },
                "pageSize": {
                  "description": "Number of results per page (default: 10, max: 50)",
                  "type": "number"
                },
                "query": {
                  "type": "string",
                  "description": "Search query string"
                }
              },
              "$schema": "http://json-schema.org/draft-07/schema#",
              "required": [
                "query"
              ],
              "additionalProperties": false
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___sage_create_question",
          "description": "Create a new question on Sage (Amazon's internal Q&A platform).\n\nThis tool allows you to post new questions to Sage through the MCP interface.\nQuestions require at least one tag or packageTag to categorize them properly.\nThe question content supports Markdown formatting for rich text, code blocks, and links.\n\nAuthentication:\n- Requires valid Midway authentication (run `mwinit` if you encounter authentication errors)\n\nCommon use cases:\n- Asking technical questions about Amazon internal tools and services\n- Seeking help with troubleshooting issues\n- Requesting best practices or guidance\n\nExample usage:\n{ \"title\": \"How to resolve Brazil dependency conflicts?\", \"contents\": \"I'm getting the following error when building my package:\\n\\n```\\nCannot resolve dependency X\\n```\\n\\nHow can I fix this?\", \"tags\": [\"brazil\", \"build-system\"] }",
          "input_schema": {
            "json": {
              "type": "object",
              "required": [
                "title",
                "contents"
              ],
              "additionalProperties": false,
              "$schema": "http://json-schema.org/draft-07/schema#",
              "properties": {
                "title": {
                  "description": "Title of the question",
                  "type": "string"
                },
                "packageTags": {
                  "type": "array",
                  "items": {
                    "type": "string"
                  },
                  "description": "Package tags to categorize the question (at least one tag or packageTag is required)"
                },
                "tags": {
                  "type": "array",
                  "description": "Tags to categorize the question (at least one tag or packageTag is required)",
                  "items": {
                    "type": "string"
                  }
                },
                "contents": {
                  "description": "Content of the question in Markdown format",
                  "type": "string"
                }
              }
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___datacentral_workbench",
          "description": "Access and query data sources in Datacentral Workbench including Andes, Redshift, and Athena. This tool enables database discovery, SQL query execution, and result retrieval.\n\nSUPPORTED OPERATIONS:\n- get_databases: List accessible databases\n- get_users_for_database: Get database users for a specific database\n- create_connection: Establish database connection with user credentials\n- get_catalog: Explore database schema structure\n- execute_query: Run SQL queries against connected database\n- check_query_status: Monitor query execution progress\n- get_query_result_url: Retrieve query results\n\nTYPICAL WORKFLOW:\n1. get_databases → 2. get_users_for_database → 3. create_connection → 4. get_catalog → 5. execute_query → 6. check_query_status → 7. get_query_result_url\n\nCOMMON PARAMETERS:\n- databaseId: Database identifier (string)\n- dbUserId: Database user identifier (string)\n- connectionId: Connection identifier (string)\n- executionId: Query execution identifier (string)\n- sql: SQL query to execute (string)",
          "input_schema": {
            "json": {
              "required": [
                "operation"
              ],
              "properties": {
                "isBatch": {
                  "type": "boolean",
                  "description": "Whether to execute SQL statements in one batch (default: false)"
                },
                "downloadAllData": {
                  "description": "Whether to download all data or just a preview (default: false)",
                  "type": "boolean"
                },
                "executionId": {
                  "type": "string",
                  "description": "Execution ID (required for check_query_status and get_query_result_url operations)"
                },
                "sql": {
                  "description": "SQL query to execute (required for execute_query operation)",
                  "type": "string"
                },
                "dbUserId": {
                  "description": "Database User ID (required for create_connection and get_catalog operations)",
                  "type": "string"
                },
                "timeout": {
                  "description": "Query timeout in milliseconds (default: 60000)",
                  "type": "number"
                },
                "connectionId": {
                  "type": "string",
                  "description": "Connection ID (required for get_catalog and execute_query operations)"
                },
                "tablePattern": {
                  "description": "Optional table pattern to filter catalog results (e.g., 'customer%')",
                  "type": "string"
                },
                "autoCommit": {
                  "type": "boolean",
                  "description": "Whether to automatically commit operations (default: true)"
                },
                "checkSyntaxEnabled": {
                  "type": "boolean",
                  "description": "Whether to validate query syntax before execution (default: true)"
                },
                "databaseId": {
                  "type": "string",
                  "description": "Database ID (required for get_users_for_database, create_connection, and get_catalog operations)"
                },
                "schemaPattern": {
                  "type": "string",
                  "description": "Optional schema pattern to filter catalog results (e.g., 'public%')"
                },
                "maxRows": {
                  "description": "Maximum number of rows to return when getting query results (default: 1000)",
                  "type": "number"
                },
                "recordLimit": {
                  "type": "number",
                  "description": "Maximum number of records to return (default: 1000)"
                },
                "operation": {
                  "description": "The operation to perform",
                  "type": "string",
                  "enum": [
                    "get_databases",
                    "get_users_for_database",
                    "create_connection",
                    "get_catalog",
                    "execute_query",
                    "check_query_status",
                    "get_query_result_url"
                  ]
                }
              },
              "$schema": "http://json-schema.org/draft-07/schema#",
              "type": "object",
              "additionalProperties": false
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___search_internal_websites",
          "description": "Search using Amazon's internal search engine is.amazon.com\n\nAvailable scopes:\n- ALL: Search across all resources (default)\n- WIKI: Internal Wiki (Amazon's central tribal knowledge repository on w.amazon.com, historically the main knowledge source containing team wikis, product documentation, personal knowledge, and experiences across various roles)\n- AWS_DOCS: AWS Documentation (official AWS service documentation and guides)\n- SAGE_HORDE: Sage/Q&A Sites (technical questions, answers, and discussions from Amazon's internal knowledge sharing platform)\n- BUILDER_HUB: BuilderHub (documentation for Amazon's internal developer tools and resources)\n- INSIDE: Inside Amazon (company news, HR policies, employee resources, and corporate information)\n- BROADCAST: Broadcast (company-wide announcements and communications)\n- IT: IT Services (IT support documentation, guides, and resources)\n- APGL: APG Library (AWS Prescriptive Guidance Library for AWS Professional Services delivery guidance)\n- EVERGREEN: Evergreen documentation platform (Specifically documentation for Amazon API or AAPI, API references, guides, etc.) hosted on console.harmony.a2z.com\n- IVY: Ivy Help (guidance for Amazon's internal talent management system, including hiring and promotions)\n- LIST_ARCHIVE: Email List Archive (archived email communications from internal mailing lists)\n- tool: Search internal tools on Spyglass (Community recommended tools, services, and content)\n\nSorting options:\n- SCORE (Default, sorts by relevance)\n- MODIFICATION_DATE (Last Modified, use with sortOrder)\n\nExamples:\n1. Basic search:\n   { \"query\": \"lambda\" }\n\n2. Search AWS docs sorted by newest first:\n   { \"query\": \"lambda\", \"scope\": \"AWS_DOCS\", \"sortBy\": \"MODIFICATION_DATE\", \"sortOrder\": \"DESC\" }\n\n3. Search Wiki with pagination:\n   { \"query\": \"brazil\", \"scope\": \"WIKI\", \"page\": \"2\" }\n\n4. Search Evergreen documentation for API guides:\n   { \"query\": \"Cards getting started\", \"scope\": \"EVERGREEN\" }\n\n5. Search Sage for technical questions about a specific topic:\n   { \"query\": \"lambda function scope stack\", \"scope\": \"SAGE_HORDE\" }\n\n6. Get detailed information about a specific scope:\n   { \"query\": \"about-scope:SAGE_HORDE\" }\n\n7. Search Wiki for team documentation:\n   { \"query\": \"Mirai team onboarding\", \"scope\": \"WIKI\" }\n\n8. Search BuilderHub for developer tools:\n   { \"query\": \"Brazil workspace setup\", \"scope\": \"BUILDER_HUB\" }\n\n9. Search Inside Amazon for HR policies:\n   { \"query\": \"remote work policy\", \"scope\": \"INSIDE\" }\n\n10. Search APG Library for AWS implementation guides:\n   { \"query\": \"migration best practices\", \"scope\": \"APGL\" }\n\n11. Search Ivy Help for promotion information:\n   { \"query\": \"promotion cycle timeline\", \"scope\": \"IVY\" }\n12. Search Internal Tools for Badge Report:\n   { \"query\": \"badge report\", \"scope\": \"tool\" }\n13. Search PCS on internal tools\n   { \"query\": \"PCS\", \"scope\": \"tool\" }\n14. Search JSON Prettifier internal tool\n   { \"query\": \"JSON Prettifier\", \"scope\": \"tool\" }\n15. Search Design Inspector in internal tools\n   { \"query\": \"Design Inspector\", \"scope\": \"tool\" }\n16. Search useful plantUML tools\n   { \"query\": \"plantUML\", \"scope\": \"tool\" }\n17. Search helpful tools for interviews on Spyglass\n   { \"query\": \"interviews\", \"scope\": \"tool\" }\n\nTips:\n- Start with the ALL scope to get a general sense of available information across all resources\n- Once you identify the likely location of information, use a specific scope for more focused results\n- Use sortBy: \"MODIFICATION_DATE\" with sortOrder: \"DESC\" to find the most recently updated content\n- For pagination, increment the page parameter to see additional results beyond the first page\n- For detailed information about a specific scope, use the query \"about-scope:<SCOPE_NAME>\" (e.g., \"about-scope:SAGE_HORDE\")",
          "input_schema": {
            "json": {
              "properties": {
                "sortBy": {
                  "description": "Sort field (SCORE, MODIFICATION_DATE)",
                  "type": "string"
                },
                "page": {
                  "type": "string",
                  "description": "Page of the search result, starting from 1"
                },
                "query": {
                  "type": "string",
                  "description": "Search query"
                },
                "scope": {
                  "type": "string",
                  "description": "Scope to search in (e.g., ALL, AWS_DOCS, WIKI, tool)"
                },
                "sortOrder": {
                  "description": "Sort order (ASC for oldest first, DESC for newest first)",
                  "type": "string",
                  "enum": [
                    "ASC",
                    "DESC"
                  ]
                }
              },
              "additionalProperties": false,
              "type": "object",
              "required": [
                "query"
              ],
              "$schema": "http://json-schema.org/draft-07/schema#"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___sage_post_answer",
          "description": "Post an answer to an existing question on Sage (Amazon's internal Q&A platform).\n\nThis tool allows you to contribute answers to questions on Sage through the MCP interface.\nThe answer content supports Markdown formatting for rich text, code blocks, and links.\n\nAuthentication:\n- Requires valid Midway authentication (run `mwinit` if you encounter authentication errors)\n\nCommon use cases:\n- Answering technical questions about Amazon internal tools and services\n- Providing code examples or troubleshooting steps\n- Sharing knowledge about internal processes\n\nExample usage:\n{ \"questionId\": 1234567, \"contents\": \"To solve this issue, you need to run:\\n\\n```bash\\nbrazil workspace merge\\n```\\n\\nThis will resolve the dependency conflicts.\" }",
          "input_schema": {
            "json": {
              "required": [
                "questionId",
                "contents"
              ],
              "additionalProperties": false,
              "$schema": "http://json-schema.org/draft-07/schema#",
              "properties": {
                "questionId": {
                  "type": "number",
                  "description": "ID of the question to answer"
                },
                "contents": {
                  "type": "string",
                  "description": "Content of the answer in Markdown format"
                }
              },
              "type": "object"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___g2s2_import_stage_version",
          "description": "Imports ion file into a specified G2S2 stage version",
          "input_schema": {
            "json": {
              "required": [
                "stageVersion",
                "filepath"
              ],
              "properties": {
                "filepath": {
                  "type": "string",
                  "description": "The ion file path to import"
                },
                "stageVersion": {
                  "description": "The stage version to import into",
                  "type": "string"
                }
              },
              "type": "object",
              "additionalProperties": false,
              "$schema": "http://json-schema.org/draft-07/schema#"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___search_katal_components",
          "description": "Search for Katal components\n\nThis tool allows you to search for Katal components using keywords.\nThe search looks through component names and tag names.\n\nExamples:\n1. Search for button components:\n```json\n{\n  \"query\": \"button\"\n}\n```",
          "input_schema": {
            "json": {
              "required": [
                "query"
              ],
              "additionalProperties": false,
              "type": "object",
              "properties": {
                "query": {
                  "type": "string",
                  "description": "Search query to find matching Katal components"
                }
              },
              "$schema": "http://json-schema.org/draft-07/schema#"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___datanet_writer",
          "description": "Create, update, and manage Datanet (also known as ETLM) resources including job profiles, jobs, and job runs. Use this tool when users mention 'Datanet', 'ETLM', or need to work with ETL jobs in the Datanet service. This tool allows you to create and edit job profiles (TRANSFORM, DATA_FEED, LOAD, METRICS, ANDES_LOAD), create and edit jobs based on these profiles, run jobs, and download job run outputs. Write operations require appropriate permissions to the specified database users, logical databases, and host groups. Job creation requires a valid profile ID, and job runs require a valid job ID. Different operations have specific required parameters and formatting requirements as detailed in the parameter descriptions.",
          "input_schema": {
            "json": {
              "additionalProperties": false,
              "properties": {
                "allowableRejects": {
                  "description": "Allowable rejects (LOAD jobs)",
                  "type": "number"
                },
                "jobType": {
                  "description": "Job type (TRANSFORM, DATA_FEED, LOAD, METRICS, ANDES_LOAD)",
                  "type": "string"
                },
                "jobDataJson": {
                  "description": "Additional job data as JSON string (ANDES_LOAD jobs)",
                  "type": "string"
                },
                "scheduleType": {
                  "type": "string",
                  "description": "Schedule type (NOT_SCHEDULED, DAILY, CRON)"
                },
                "jobData": {
                  "type": "string",
                  "description": "JSON string containing the job data. Must include required fields like profileId, type, description, owner, group, etc.\n      \nExample for TRANSFORM job:\n{\n  \"profileId\": 13401437,\n  \"type\": \"TRANSFORM\",\n  \"description\": \"TRANSFORM job description\",\n  \"owner\": \"your-alias\",\n  \"group\": \"your-group-name\",\n  \"dbUser\": \"your-db-user\",\n  \"logicalDB\": \"your-logical-db\",\n  \"timezone\": \"America/Los_Angeles\",\n  \"priority\": \"NORMAL\",\n  \"schedule\": {\n    \"type\": \"NOT_SCHEDULED\"\n  },\n  \"status\": \"ACTIVE\",\n  \"hostGroup\": \"GenericHosts\",\n  \"partitionKeys\": [\n    {\n      \"partitionTypeId\": \"REGION\",\n      \"partitionValue\": 1\n    }\n  ]\n}\n\nFor create_job operation, the jobData must include:\n\n1. Required fields for all job types:\n   - __type: Must match the job type (see mapping below)\n   - profileId: The profile ID to create the job from\n   - type: Job type (must match profile type, e.g., \"TRANSFORM\")\n   - description: Job description\n   - owner: Job owner (your alias)\n   - group: Group name for permissions\n   - timezone: Timezone (e.g., \"America/Los_Angeles\")\n   - priority: Job priority (\"LOW\", \"NORMAL\", \"HIGHEST\")\n   - schedule: Schedule configuration object with specific format based on schedule type:\n     - Not Scheduled: { \n         \"__type\": \"NotScheduled:http://internal.amazon.com/coral/com.amazon.datanet.model/\", \n         \"type\": \"NOT_SCHEDULED\" \n       }\n     - Daily Schedule: { \n         \"__type\": \"Daily:http://internal.amazon.com/coral/com.amazon.datanet.model/\", \n         \"type\": \"DAILY\", \n         \"dayPreferences\": [\n           {\n             \"datasetDay\": \"MONDAY\", \n             \"deliveryDay\": \"TUESDAY\", \n             \"deliveryTime\": \"08:00:00\"\n           }\n         ] \n       }\n     - Intraday Schedule: { \n         \"__type\": \"Intraday:http://internal.amazon.com/coral/com.amazon.datanet.model/\", \n         \"type\": \"INTRADAY\", \n         \"time\": [\"02:00:00\", \"04:00:00\", \"06:00:00\", \"08:00:00\"]\n       }\n     - Monthly Schedule: { \n         \"__type\": \"Monthly:http://internal.amazon.com/coral/com.amazon.datanet.model/\", \n         \"type\": \"MONTHLY\", \n         \"monthDay\": 5\n       }\n     - Cron Schedule: { \n         \"__type\": \"CronSchedule:http://internal.amazon.com/coral/com.amazon.datanet.model/\", \n         \"type\": \"CRON\", \n         \"cronExpression\": \"0 17 * * 2\" \n       }\n   - status: Job status (\"ACTIVE\", \"INACTIVE\", \"DISABLED\")\n   - hostGroup: Host group (typically \"GenericHosts\")\n   - partitionKeys: Array of partition key objects, for example:\n     [\n       {\n         \"partitionTypeId\": \"REGION\",\n         \"partitionValue\": 1\n       },\n       {\n         \"partitionTypeId\": \"LEGAL_ENTITY_ID\",\n         \"partitionValue\": 101\n       }\n     ]\n\n2. Job type mapping by profile type:\n   - TRANSFORM/DATA_FEED: __type: \"ExtractJob:http://internal.amazon.com/coral/com.amazon.datanet.model/\"\n     Additional required fields:\n     - dbUser: Database user (e.g., \"amzn:cdo:datanet-dbuser:your_db_user\")\n     - logicalDB: Logical database name (e.g., \"findbrs01\")\n   \n   - LOAD: __type: \"LoadJob:http://internal.amazon.com/coral/com.amazon.datanet.model/\"\n     Additional required fields:\n     - dbUser: Database user (e.g., \"amzn:cdo:datanet-dbuser:your_db_user\")\n     - allowZeroRows: Object with days of week, for example:\n       {\n         \"MONDAY\": true, \"TUESDAY\": true, \"WEDNESDAY\": true, \"THURSDAY\": true,\n         \"FRIDAY\": true, \"SATURDAY\": true, \"SUNDAY\": true\n       }\n     - allowableRejects: Number (typically 0)\n     - validateRowCount: Boolean (typically false)\n   \n   - METRICS: __type: \"ConversionJob:http://internal.amazon.com/coral/com.amazon.datanet.model/\"\n     Additional required fields:\n     - generateNFiles: Number (typically 1)\n     - mapping: JSON string with tab mapping configuration, for example:\n       \"{\"tab mapping\":{\"Sample Tab\":333720},\"cutoff\":{},\"version\":1}\"\n   \n   - ANDES_LOAD: __type: \"ExtractJob:http://internal.amazon.com/coral/com.amazon.datanet.model/\"\n     Additional required fields:\n     - jobData: JSON string with configuration, for example:\n       \"{\"allowableRejects\":null,\"allowZeroRowsDays\":null}\"\n\n3. Schedule types:\n   - Not Scheduled: { \"__type\": \"NotScheduled:http://internal.amazon.com/coral/com.amazon.datanet.model/\", \"type\": \"NOT_SCHEDULED\" }\n   - Daily: { \"__type\": \"Daily:http://internal.amazon.com/coral/com.amazon.datanet.model/\", \"type\": \"DAILY\", \"dayPreferences\": [{\"datasetDay\": \"MONDAY\", \"deliveryDay\": \"TUESDAY\", \"deliveryTime\": \"00:00\"}] }\n   - Intraday: { \"__type\": \"Intraday:http://internal.amazon.com/coral/com.amazon.datanet.model/\", \"type\": \"INTRADAY\", \"time\": [\"02:00:00\", \"04:00:00\", \"06:00:00\", \"08:00:00\"] }\n   - Monthly: { \"__type\": \"Monthly:http://internal.amazon.com/coral/com.amazon.datanet.model/\", \"type\": \"MONTHLY\", \"monthDay\": 5 }\n   - Cron: { \"__type\": \"CronSchedule:http://internal.amazon.com/coral/com.amazon.datanet.model/\", \"type\": \"CRON\", \"cronExpression\": \"0 17 * * 2\" }\n\nFor edit_job operation, the jobData must follow the correct structure:\n\n1. For schedule updates:\n   - Use a nested 'schedule' object with the correct __type and type fields\n   - For CRON schedules: { \"schedule\": { \"__type\": \"CronSchedule:http://internal.amazon.com/coral/com.amazon.datanet.model/\", \"type\": \"CRON\", \"cronExpression\": \"0 17 * * 2\" } }\n   - For DAILY schedules: { \"schedule\": { \"__type\": \"DailySchedule:http://internal.amazon.com/coral/com.amazon.datanet.model/\", \"type\": \"DAILY\", \"dayPreferences\": [{\"datasetDay\": \"MONDAY\", \"deliveryDay\": \"TUESDAY\", \"deliveryTime\": \"08:00:00\"}] } }\n   - For NOT_SCHEDULED: { \"schedule\": { \"__type\": \"NotScheduled:http://internal.amazon.com/coral/com.amazon.datanet.model/\", \"type\": \"NOT_SCHEDULED\" } }\n\n2. For other common fields:\n   - description: String description of the job\n   - priority: String value (e.g., \"NORMAL\", \"LOW\", \"HIGH\")\n   - status: String value (e.g., \"ACTIVE\", \"INACTIVE\")\n   - timezone: String timezone (e.g., \"America/Los_Angeles\")\n   \nExample for creating a TRANSFORM job:\n{\n  \"__type\": \"ExtractJob:http://internal.amazon.com/coral/com.amazon.datanet.model/\",\n  \"profileId\": 13401437,\n  \"type\": \"TRANSFORM\",\n  \"description\": \"TRANSFORM job description\",\n  \"owner\": \"your-alias\",\n  \"group\": \"your-group-name\",\n  \"dbUser\": \"your-db-user\",\n  \"logicalDB\": \"your-logical-db\",\n  \"timezone\": \"America/Los_Angeles\",\n  \"priority\": \"NORMAL\",\n  \"schedule\": {\n    \"__type\": \"NotScheduled:http://internal.amazon.com/coral/com.amazon.datanet.model/\",\n    \"type\": \"NOT_SCHEDULED\"\n  },\n  \"status\": \"ACTIVE\",\n  \"hostGroup\": \"GenericHosts\",\n  \"partitionKeys\": [\n    {\n      \"partitionTypeId\": \"REGION\",\n      \"partitionValue\": 1\n    }\n  ]\n}"
                },
                "generateNFiles": {
                  "description": "Generate N Files (METRICS jobs)",
                  "type": "number"
                },
                "status": {
                  "type": "string",
                  "description": "Job status (ACTIVE, INACTIVE)"
                },
                "validateRowCount": {
                  "type": "boolean",
                  "description": "Validate row count (LOAD jobs)"
                },
                "jobRunId": {
                  "type": "string",
                  "description": "ID of the job run. Required for download_job_run_output."
                },
                "outputPath": {
                  "description": "File path to save the output. Required for download_job_run_output.",
                  "type": "string"
                },
                "mimeType": {
                  "description": "Format of the output (plain, text, excel, html). Default: plain",
                  "type": "string"
                },
                "timezone": {
                  "description": "Timezone (e.g., America/Los_Angeles)",
                  "type": "string"
                },
                "encoding": {
                  "type": "string",
                  "description": "Character encoding for the output (UTF8, SJIS, ISO8859_1). Default: UTF8"
                },
                "dayPreferencesJson": {
                  "description": "JSON string of day preferences for DAILY schedule",
                  "type": "string"
                },
                "profileId": {
                  "description": "Profile ID for the job",
                  "type": "string"
                },
                "jobId": {
                  "description": "ID of the job. Required for edit_job and run_job.",
                  "type": "string"
                },
                "group": {
                  "type": "string",
                  "description": "Job group"
                },
                "mapping": {
                  "type": "string",
                  "description": "Mapping configuration (METRICS jobs)"
                },
                "operation": {
                  "description": "The operation to perform",
                  "enum": [
                    "create_job_profile",
                    "edit_job_profile",
                    "create_job",
                    "edit_job",
                    "run_job",
                    "download_job_run_output"
                  ],
                  "type": "string"
                },
                "priority": {
                  "type": "string",
                  "description": "Job priority (NORMAL, LOW, HIGH)"
                },
                "profileData": {
                  "description": "JSON string containing the profile data. Required for create_job_profile and edit_job_profile.\n      \nFor create_job_profile operation, the profileData must include:\n\n1. Required fields for all profile types:\n   - __type: Must match the profile type (see mapping below)\n   - type: Profile type (e.g., \"TRANSFORM\", \"DATA_FEED\", \"LOAD\")\n   - description: Profile description\n   - status: Profile status (\"ACTIVE\", \"INACTIVE\")\n   - group: Group name for permissions\n\n2. Profile type specific fields:\n   - TRANSFORM/DATA_FEED: \n     - __type: \"TransformJobProfile:http://internal.amazon.com/coral/com.amazon.datanet.model/\" or \"DataFeedJobProfile:http://internal.amazon.com/coral/com.amazon.datanet.model/\"\n     - sql: SQL query for the profile (e.g., \"SELECT customer_id, UPPER(customer_name) as customer_name_upper FROM customers;\")\n     - output: (Optional) Output configuration object, for example:\n       {\n         \"__type\": \"FileTemplate:http://internal.amazon.com/coral/com.amazon.datanet.model/\",\n         \"fileTemplate\": \"/path/to/output/file_{JOBRUN_DETAILS}.txt\"\n       }\n   \n   - LOAD:\n     - __type: \"FileLoadJobProfile:http://internal.amazon.com/coral/com.amazon.datanet.model/\"\n     - logicalDb: Logical database name (e.g., \"findbrs01\")\n     - qualifiedTable: Object with tableName and tableOwner, for example:\n       {\n         \"tableName\": \"TARGET_TABLE\",\n         \"tableOwner\": \"TABLE_OWNER\",\n         \"tableVariant\": null\n       }\n     - inputs: Array of input file templates, for example:\n       [{\n         \"__type\": \"FileTemplate:http://internal.amazon.com/coral/com.amazon.datanet.model/\",\n         \"fileTemplate\": \"/path/to/input/data_{JOBRUN_DETAILS}.txt\"\n       }]\n     - loadOption: Load option configuration, for example:\n       {\n         \"__type\": \"InsertLoadOption:http://internal.amazon.com/coral/com.amazon.datanet.model/\",\n         \"loadSequential\": false,\n         \"replaceOption\": \"PARTITION\"\n       }\n     - filterSql: SQL filter (can be \"1=1\" if not needed)\n   \n   - METRICS:\n     - __type: \"MetricsJobProfile:http://internal.amazon.com/coral/com.amazon.datanet.model/\"\n     - inputFileTemplate: Template file path (e.g., \"METRICS_TEMPLATE.xlsx\")\n     - outputDataset: Output dataset path (e.g., \"Metrics_Report_{JOBRUN_DETAILS}.xlsx\")\n     - output: Output configuration object, for example:\n       {\n         \"__type\": \"FileTemplate:http://internal.amazon.com/coral/com.amazon.datanet.model/\",\n         \"fileTemplate\": \"Metrics_Report_{JOBRUN_DETAILS}.xlsx\"\n       }\n   \n   - ANDES_LOAD:\n     - type: \"ANDES_LOAD\"\n     - profileData: JSON string with Andes table configuration, for example:\n       \"{\"tableOwner\":\"andes-provider-uuid\",\"tableName\":\"target-table-name\",\"partitionSchemeName\":\"partition-scheme-uuid\",\"loadType\":\"APPEND\",\"loadOption\":\"UPSERT\",\"inputFileTemplates\":[\"/path/to/input_{JOBRUN_DETAILS}.tsv\"]}\"\n\nExample for creating a TRANSFORM profile:\n{\n  \"__type\": \"TransformJobProfile:http://internal.amazon.com/coral/com.amazon.datanet.model/\",\n  \"type\": \"TRANSFORM\",\n  \"description\": \"Transform customer data\",\n  \"sql\": \"SELECT customer_id, UPPER(customer_name) as customer_name_upper FROM customers;\",\n  \"status\": \"ACTIVE\",\n  \"group\": \"your-group-name\"\n}",
                  "type": "string"
                },
                "logicalDB": {
                  "type": "string",
                  "description": "Logical database"
                },
                "dbUser": {
                  "description": "Database user",
                  "type": "string"
                },
                "allowZeroRowsJson": {
                  "description": "JSON string for allow zero rows configuration (LOAD jobs)",
                  "type": "string"
                },
                "profileType": {
                  "description": "Type of the profile (e.g., TRANSFORM, DATA_FEED, LOAD, METRICS, ANDES_LOAD). Required for profile operations.",
                  "type": "string"
                },
                "datasetDate": {
                  "type": "string",
                  "description": "Dataset date in YYYY-MM-DD format. Required for run_job."
                },
                "hostGroup": {
                  "type": "string",
                  "description": "Host group"
                },
                "owner": {
                  "type": "string",
                  "description": "Job owner"
                },
                "cronExpression": {
                  "type": "string",
                  "description": "Cron expression for CRON schedule"
                },
                "jobProfileId": {
                  "type": "string",
                  "description": "ID of the job profile. Required for edit_job_profile."
                },
                "description": {
                  "type": "string",
                  "description": "Job description"
                },
                "partitionKeysJson": {
                  "type": "string",
                  "description": "Partition keys as JSON string"
                },
                "scheduled": {
                  "description": "Whether the job run is scheduled (defaults to false)",
                  "type": "boolean"
                }
              },
              "type": "object",
              "required": [
                "operation"
              ],
              "$schema": "http://json-schema.org/draft-07/schema#"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___reassign_ticket_by_cti",
          "description": "This tool reassigns a ticket by specifying a new CTI (Category/Type/Item) path.",
          "input_schema": {
            "json": {
              "additionalProperties": false,
              "properties": {
                "item": {
                  "type": "string",
                  "description": "The CTI item"
                },
                "ticketId": {
                  "description": "The ID of the ticket to reassign (e.g., 'P12345678' or 'T12345678')",
                  "type": "string"
                },
                "category": {
                  "description": "The CTI category",
                  "type": "string"
                },
                "requestId": {
                  "type": [
                    "string",
                    "number"
                  ],
                  "description": "Optional request identifier for JSON-RPC correlation and debugging."
                },
                "type": {
                  "description": "The CTI type",
                  "type": "string"
                }
              },
              "$schema": "http://json-schema.org/draft-07/schema#",
              "type": "object",
              "required": [
                "ticketId",
                "category",
                "type",
                "item"
              ]
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___genai_poweruser_list_knowledge",
          "description": "Generate organized inventories of documents stored in the knowledge repository. This tool can list all documents or focus on specific folders, with options for recursive directory traversal and depth control. Returns document paths and titles, enabling systematic navigation of the knowledge structure.",
          "input_schema": {
            "json": {
              "properties": {
                "folder": {
                  "description": "The folder path to list documents from",
                  "type": "string"
                },
                "recursive": {
                  "description": "Whether to include documents in subfolders",
                  "type": "boolean"
                },
                "depth": {
                  "default": 5,
                  "type": "number",
                  "description": "How many levels deep to traverse"
                }
              },
              "type": "object",
              "$schema": "http://json-schema.org/draft-07/schema#",
              "additionalProperties": false
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___rtla_fetch_logs",
          "description": "Fetch logs from RTLA (Real-Time Log Analysis) API. This tool allows you to retrieve log entries based on organization, affected type, time range, and filter expressions. The maximum time range supported is 12 hours from the start time. Useful for troubleshooting system issues, analyzing error patterns, and monitoring application health.",
          "input_schema": {
            "json": {
              "additionalProperties": false,
              "type": "object",
              "properties": {
                "anchor": {
                  "default": "Ending",
                  "type": "string",
                  "description": "Anchor position (e.g., \"Ending\", \"Beginning\")"
                },
                "searchField": {
                  "type": "string",
                  "default": "org",
                  "description": "Search field type (default: \"org\")"
                },
                "affectedType": {
                  "type": "string",
                  "description": "Type of affected logs to retrieve (e.g., \"FATAL\", \"NONFATAL\")"
                },
                "startTime": {
                  "type": "string",
                  "description": "Start time in ISO 8601 format with timezone (e.g., 2025-05-11T11:31:16-04:00)"
                },
                "endTime": {
                  "type": "string",
                  "description": "End time in ISO 8601 format with timezone (e.g., 2025-05-11T12:31:16-04:00)"
                },
                "timeZone": {
                  "default": "GMT&customTimeZoneOffset",
                  "description": "Time zone (e.g., \"US/Pacific\")",
                  "type": "string"
                },
                "filterExpression": {
                  "type": "string",
                  "description": "Filter expression for log filtering (e.g., \"(pageType eq 'uscbcc-ecm-paybill')\")"
                },
                "org": {
                  "type": "string",
                  "description": "Organization identifier (e.g., \"CWCBCCECMPROD\")"
                },
                "identifyAdditionalOrgs": {
                  "default": true,
                  "description": "Whether to identify additional organizations",
                  "type": "boolean"
                }
              },
              "required": [
                "org",
                "affectedType",
                "startTime",
                "endTime"
              ],
              "$schema": "http://json-schema.org/draft-07/schema#"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___cradle_list_profiles",
          "description": "List Cradle profiles with optional filtering by account and type.",
          "input_schema": {
            "json": {
              "type": "object",
              "$schema": "http://json-schema.org/draft-07/schema#",
              "required": [
                "accountName"
              ],
              "additionalProperties": false,
              "properties": {
                "sortOrder": {
                  "type": "string",
                  "description": "Sort order (asc or desc)"
                },
                "profileType": {
                  "description": "Profile type filter (DRYAD_SPARK or DRYAD_BLASTFURNACE)",
                  "type": "string"
                },
                "accountName": {
                  "description": "Account name for filtering profiles (e.g., datanet)",
                  "type": "string"
                },
                "sortCol": {
                  "type": "string",
                  "description": "Column to sort by (e.g., lastUpdatedDate)"
                },
                "pageSize": {
                  "description": "Number of items per page",
                  "type": "number"
                },
                "pageToken": {
                  "type": "string",
                  "description": "Token for pagination"
                },
                "limit": {
                  "description": "Maximum number of results to return",
                  "type": "number"
                }
              }
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___sim_add_tag",
          "description": "Add a tag to an existing SIM issue.\nThe issue ID can be either the P-number (e.g., P12345678) or the alias (e.g., CFN-12345).\nThe assignee should be a valid kerberos username without the @ANT.AMAZON.COM suffix.",
          "input_schema": {
            "json": {
              "additionalProperties": false,
              "$schema": "http://json-schema.org/draft-07/schema#",
              "type": "object",
              "properties": {
                "issueId": {
                  "type": "string",
                  "description": "Issue ID or alias (e.g., P12345678 or CFN-12345)"
                },
                "tag": {
                  "type": "string",
                  "description": "Tag to add to the issue"
                }
              },
              "required": [
                "issueId",
                "tag"
              ]
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___sage_add_comment",
          "description": "Add a comment to a post on Sage (Amazon's internal Q&A platform).\n\nThis tool allows you to comment on questions or answers on Sage through the MCP interface.\nComments are useful for requesting clarification, providing additional context, or suggesting improvements.\nComments use plain text format (no Markdown support).\n\nAuthentication:\n- Requires valid Midway authentication (run `mwinit` if you encounter authentication errors)\n\nCommon use cases:\n- Asking for clarification on a question or answer\n- Providing additional context or information\n- Suggesting improvements or alternatives\n\nExample usage:\n{ \"postId\": 1234567, \"contents\": \"Could you also explain how this works with custom dependencies?\" }",
          "input_schema": {
            "json": {
              "properties": {
                "contents": {
                  "type": "string",
                  "description": "Content of the comment in plain text"
                },
                "postId": {
                  "type": "number",
                  "description": "ID of the post (question or answer) to comment on"
                }
              },
              "$schema": "http://json-schema.org/draft-07/schema#",
              "type": "object",
              "additionalProperties": false,
              "required": [
                "postId",
                "contents"
              ]
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___cradle_search_jobs",
          "description": "Search for Cradle jobs across all profiles.",
          "input_schema": {
            "json": {
              "required": [
                "searchTerm"
              ],
              "$schema": "http://json-schema.org/draft-07/schema#",
              "type": "object",
              "properties": {
                "profileId": {
                  "type": "string",
                  "description": "UUID of the job profile for filtering"
                },
                "pageSize": {
                  "description": "Number of items per page",
                  "type": "number"
                },
                "searchTerm": {
                  "description": "Search term for job name searches",
                  "type": "string"
                },
                "limit": {
                  "type": "number",
                  "description": "Maximum number of results to return"
                },
                "pageToken": {
                  "description": "Token for pagination",
                  "type": "string"
                }
              },
              "additionalProperties": false
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___read_permissions",
          "description": "Read team information from Amazon's internal permissions system.\n\nThis tool allows you to retrieve detailed information about team memberships,\noverrides, and rules from permissions.amazon.com team pages.\n\nYou MUST specify which tables OR rule sections to include in the response.\nAt least one of these parameters must be provided with at least one option selected.\nThe tool will only retrieve the specified tables and rule sections.\n\nAvailable tables:\n- additional_overrides: Additional Members overrides table\n- deny_overrides: Denied Members overrides table\n- team_membership: Team Membership table (large table, slow to retrieve)\n- team_audit: Team Audit log table (very large table, very slow to retrieve)\n\nAvailable rule sections:\n- rule_membership: Membership rules section\n- rule_additional_overrides: Additional Members overrides rules section\n\nFor large tables (especially team_membership and team_audit), you can use the\nmaxPages parameter to limit the number of pages processed and prevent timeouts.\nYou can also use tableFilters to narrow down the results.",
          "input_schema": {
            "json": {
              "properties": {
                "ruleSections": {
                  "type": "array",
                  "items": {
                    "type": "string",
                    "enum": [
                      "rule_membership",
                      "rule_additional_overrides"
                    ]
                  },
                  "description": "List of specific rule sections to include. At least one table or rule section must be specified."
                },
                "maxPages": {
                  "description": "Maximum number of pages to process per table. Use for very large tables to prevent timeouts.",
                  "exclusiveMinimum": 0,
                  "type": "integer"
                },
                "teamUrl": {
                  "format": "uri",
                  "description": "URL of the permissions team page to read",
                  "type": "string"
                },
                "tableFilters": {
                  "additionalProperties": {
                    "type": "object",
                    "additionalProperties": false,
                    "properties": {
                      "query": {
                        "anyOf": [
                          {
                            "type": "string",
                            "description": "Text to search for in the table rows"
                          },
                          {
                            "items": {
                              "type": "string"
                            },
                            "type": "array",
                            "description": "Multiple terms to search for in the table rows (combined with OR logic)"
                          }
                        ],
                        "description": "Text or array of texts to search for in the table rows"
                      },
                      "threshold": {
                        "description": "Fuzzy match threshold (0-1). Lower = stricter match. Default is 0.3",
                        "default": 0.3,
                        "minimum": 0,
                        "maximum": 1,
                        "type": "number"
                      }
                    },
                    "required": [
                      "query"
                    ]
                  },
                  "description": "Filters to apply to specific tables. Each filter contains a query string or array of query strings and optional threshold.",
                  "propertyNames": {
                    "enum": [
                      "additional_overrides",
                      "deny_overrides",
                      "team_membership",
                      "team_audit"
                    ]
                  },
                  "type": "object"
                },
                "tables": {
                  "items": {
                    "enum": [
                      "additional_overrides",
                      "deny_overrides",
                      "team_membership",
                      "team_audit"
                    ],
                    "type": "string"
                  },
                  "description": "List of specific tables to include. At least one table or rule section must be specified.",
                  "type": "array"
                }
              },
              "additionalProperties": false,
              "required": [
                "teamUrl"
              ],
              "$schema": "http://json-schema.org/draft-07/schema#",
              "type": "object"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___policy_engine_get_risk",
          "description": "Access Amazon Policy Engine risk information for a specific entity. This tool allows you to retrieve detailed information about a specific risk or violation from Policy Engine.",
          "input_schema": {
            "json": {
              "required": [
                "entityId"
              ],
              "$schema": "http://json-schema.org/draft-07/schema#",
              "properties": {
                "entityId": {
                  "description": "Entity ID of the risk/violation to view details for",
                  "type": "string"
                }
              },
              "additionalProperties": false,
              "type": "object"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___search_internal_issues",
          "description": "Search internal issues from https://i.amazon.com/.\nIssues generally are used to manage Amazon's internal development efforts, this includes reporting of bugs, \nrequest for features, roadmaps, managed tasks for Agile development (ex. Sprint, Kanban board tasks).\n\n\nSome value query examples:\n\n* keyword only: Mirai \n\n* keyword AND status: (Mirai team)+status:(Open)\n\n* requested by user: requester:(sshli)\n\n* assigned to user: assignee:(sshli)\n",
          "input_schema": {
            "json": {
              "type": "object",
              "additionalProperties": false,
              "required": [
                "query"
              ],
              "properties": {
                "query": {
                  "description": "Search query for internal issues",
                  "type": "string"
                }
              },
              "$schema": "http://json-schema.org/draft-07/schema#"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___pippin_list_projects",
          "description": "Lists all available Pippin design projects",
          "input_schema": {
            "json": {
              "properties": {
                "statuses": {
                  "type": "string",
                  "description": "Project statuses to filter by"
                },
                "nextToken": {
                  "type": "string",
                  "description": "Pagination token"
                },
                "user": {
                  "type": "string",
                  "description": "User to filter by"
                },
                "maxResults": {
                  "type": "number",
                  "description": "Maximum number of results to return"
                }
              },
              "type": "object",
              "$schema": "http://json-schema.org/draft-07/schema#",
              "additionalProperties": false
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___get_thread_folders_quip",
          "description": "Get folders containing a Quip thread (V2 API)\n\nThis tool retrieves information about folders that contain a specific thread.\nIt uses the V2 API which provides more comprehensive folder information.\n\nYou can provide one of the following:\n- The thread ID\n- The thread's secret path\n- The full Quip URL (e.g., https://quip-amazon.com/abc/Doc)\n\nThe secret path can be found in the URL of a thread.\nFor example, in 'https://quip.com/3fs7B2leat8/TrackingDocument', the secret path is '3fs7B2leat8'.\n\nExamples:\n```json\n{\n  \"threadId\": \"3fs7B2leat8\"\n}\n```\n\n```json\n{\n  \"threadId\": \"https://quip-amazon.com/abc/Doc\"\n}\n```",
          "input_schema": {
            "json": {
              "additionalProperties": false,
              "type": "object",
              "properties": {
                "threadId": {
                  "description": "The thread ID, secret path, or full Quip URL",
                  "type": "string"
                }
              },
              "required": [
                "threadId"
              ],
              "$schema": "http://json-schema.org/draft-07/schema#"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___create_folder_quip",
          "description": "Create a new Quip folder\n\nThis tool creates a new folder in Quip.\nYou can optionally specify a parent folder to create a subfolder.\n\nExamples:\n1. Create a root-level folder:\n```json\n{\n  \"title\": \"New Project Folder\"\n}\n```\n\n2. Create a subfolder:\n```json\n{\n  \"title\": \"Documentation\",\n  \"parentFolderId\": \"ABCDEF123456\"\n}\n```\n",
          "input_schema": {
            "json": {
              "properties": {
                "parentFolderId": {
                  "type": "string",
                  "description": "ID of parent folder (if not provided, creates at root level)"
                },
                "title": {
                  "description": "Title of the new folder",
                  "type": "string"
                }
              },
              "additionalProperties": false,
              "$schema": "http://json-schema.org/draft-07/schema#",
              "required": [
                "title"
              ],
              "type": "object"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___sim_add_comment",
          "description": "Add a comment to an existing SIM issue.\nThis tool allows adding a plain text comment to an issue identified by its ID or alias.\nThe issue ID can be either the P-number (e.g., P12345678) or the alias (e.g., CFN-12345).",
          "input_schema": {
            "json": {
              "additionalProperties": false,
              "type": "object",
              "properties": {
                "message": {
                  "type": "string",
                  "description": "Comment text to add to the issue"
                },
                "issueId": {
                  "description": "Issue ID or alias (e.g., P12345678 or CFN-12345)",
                  "type": "string"
                }
              },
              "$schema": "http://json-schema.org/draft-07/schema#",
              "required": [
                "issueId",
                "message"
              ]
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___sim_add_label",
          "description": "Add a label to an existing SIM issue.\nThe issue ID can be either the P-number (e.g., P12345678) or the alias (e.g., CFN-12345).\nLabels help categorize issues and can be used for filtering and organization.",
          "input_schema": {
            "json": {
              "type": "object",
              "properties": {
                "issueId": {
                  "description": "Issue ID or alias (e.g., P12345678 or CFN-12345)",
                  "type": "string"
                },
                "label": {
                  "type": "string",
                  "description": "Label to add to the issue"
                }
              },
              "required": [
                "issueId",
                "label"
              ],
              "additionalProperties": false,
              "$schema": "http://json-schema.org/draft-07/schema#"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___search_eventstream",
          "description": "Search Amazon internal Eventstream for operational events to identify potential causes of customer-impacting issues. Supports filtering by 47+ event types including Apollo Deployment, Lambda Deployment, Weblab Activation, G2S2, Large Scale Event, and many others. Use list_eventstream_parameters tool to see all available options.",
          "input_schema": {
            "json": {
              "type": "object",
              "additionalProperties": false,
              "properties": {
                "query": {
                  "properties": {
                    "tokens": {
                      "description": "Array of filter conditions",
                      "items": {
                        "properties": {
                          "operator": {
                            "type": "string",
                            "description": "Comparison operator",
                            "enum": [
                              "=",
                              "!=",
                              "contains"
                            ]
                          },
                          "propertyKey": {
                            "type": "string",
                            "description": "Property key to filter on"
                          },
                          "value": {
                            "type": "string",
                            "description": "Value to match against"
                          }
                        },
                        "required": [
                          "propertyKey",
                          "operator",
                          "value"
                        ],
                        "type": "object",
                        "additionalProperties": false
                      },
                      "type": "array"
                    },
                    "operation": {
                      "type": "string",
                      "enum": [
                        "and",
                        "or"
                      ],
                      "description": "Logical operator for combining tokens"
                    }
                  },
                  "type": "object",
                  "required": [
                    "tokens",
                    "operation"
                  ],
                  "description": "Custom query tokens for advanced filtering",
                  "additionalProperties": false
                },
                "offset": {
                  "type": "number",
                  "minimum": 0,
                  "description": "Number of events to skip for pagination (default: 0)"
                },
                "cti": {
                  "type": "string",
                  "description": "CTI (Category / Type / Item) identifier to filter by"
                },
                "maxResults": {
                  "description": "Maximum number of events to return (1-1000, default: 50)",
                  "minimum": 1,
                  "type": "number",
                  "maximum": 1000
                },
                "dateRange": {
                  "description": "Date range for event search (defaults to last hour)",
                  "required": [
                    "type"
                  ],
                  "type": "object",
                  "additionalProperties": false,
                  "properties": {
                    "endDate": {
                      "description": "End date for absolute range (ISO format)",
                      "type": "string"
                    },
                    "startDate": {
                      "type": "string",
                      "description": "Start date for absolute range (ISO format)"
                    },
                    "unit": {
                      "enum": [
                        "minute",
                        "hour",
                        "day",
                        "week"
                      ],
                      "description": "Unit for relative date range",
                      "type": "string"
                    },
                    "type": {
                      "type": "string",
                      "enum": [
                        "relative",
                        "absolute"
                      ],
                      "description": "Type of date range"
                    },
                    "amount": {
                      "type": "number",
                      "description": "Amount for relative date range"
                    }
                  }
                },
                "eventTypes": {
                  "description": "Event types to filter by (e.g., 'Apollo Deployment', 'Lambda Deployment', 'Weblab Activation', 'G2S2', 'Large Scale Event'). See README.md for complete list of 47+ supported event types.",
                  "type": "array",
                  "items": {
                    "type": "string"
                  }
                },
                "bindle": {
                  "description": "Bindle (application permissions bundle) identifier to filter by",
                  "type": "string"
                }
              },
              "$schema": "http://json-schema.org/draft-07/schema#"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___lookup_user_coding_activity_summary",
          "description": "Looks up coding activity summary for a given user by their user login/alias",
          "input_schema": {
            "json": {
              "type": "object",
              "required": [
                "alias"
              ],
              "additionalProperties": false,
              "$schema": "http://json-schema.org/draft-07/schema#",
              "properties": {
                "start_time": {
                  "type": "string",
                  "description": "Optional start date in YYYY-MM-DD format"
                },
                "end_time": {
                  "type": "string",
                  "description": "Optional end date in YYYY-MM-DD format"
                },
                "alias": {
                  "description": "Alias or login for the user to look up",
                  "type": "string"
                }
              }
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___get_recent_messages_quip",
          "description": "Get recent messages from a Quip thread\n\nThis tool retrieves the most recent messages for a given Quip thread.\nYou can filter and sort the messages using various parameters.\n\nExamples:\n1. Get recent messages:\n```json\n{\n  \"threadIdOrUrl\": \"https://quip-amazon.com/abc/Doc\"\n}\n```\n\n2. Get recent messages with count:\n```json\n{\n  \"threadIdOrUrl\": \"https://quip-amazon.com/abc/Doc\",\n  \"count\": 10\n}\n```\n\n3. Get recent edit messages:\n```json\n{\n  \"threadIdOrUrl\": \"https://quip-amazon.com/abc/Doc\",\n  \"messageType\": \"edit\"\n}\n```",
          "input_schema": {
            "json": {
              "required": [
                "threadIdOrUrl"
              ],
              "additionalProperties": false,
              "type": "object",
              "properties": {
                "count": {
                  "type": "number",
                  "description": "Number of messages to return (1-100, default 25)"
                },
                "sortedBy": {
                  "enum": [
                    "ASC",
                    "DESC"
                  ],
                  "description": "Sort order for messages",
                  "type": "string"
                },
                "maxCreatedUsec": {
                  "type": "number",
                  "description": "UNIX timestamp in microseconds for messages created at and before"
                },
                "updatedSinceUsec": {
                  "description": "UNIX timestamp in microseconds for messages updated at and after",
                  "type": "number"
                },
                "messageType": {
                  "description": "Type of messages to return",
                  "type": "string",
                  "enum": [
                    "message",
                    "edit"
                  ]
                },
                "lastUpdatedSinceUsec": {
                  "type": "number",
                  "description": "UNIX timestamp in microseconds for messages updated before"
                },
                "sortBy": {
                  "description": "Alias for sortedBy",
                  "type": "string",
                  "enum": [
                    "ASC",
                    "DESC"
                  ]
                },
                "threadIdOrUrl": {
                  "description": "The thread ID or Quip URL to get messages from",
                  "type": "string"
                }
              },
              "$schema": "http://json-schema.org/draft-07/schema#"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___add_comment_quip",
          "description": "Add a comment to a Quip document\n\nThis tool allows you to add a comment to a specified Quip document or thread.\nComments appear in the thread's conversation panel and are visible to all document collaborators.\nThe comment will be attributed to the owner of the API token.\n\nParameters:\n- threadIdOrUrl: (Required) The Quip document/thread ID or URL to add a comment to\n- content: (Required) The comment message text to add\n- section_id: ID of a document section to comment on\n\nNotes:\n- Plain text only, no formatting or HTML is supported\n- Comments cannot be edited or deleted through the Quip API: These operations are not supported\n- Maximum length is 1MB (though practical messages are typically much shorter)\n- Only one of section_id or annotation_id can be provided\n- annotation_id is retrieved as a response of the get_recent_messages_quip tool\n- Manually creating a link to a quip section gives a response like : https://quip-amazon.com/bpVtAZ8LB0b4/Quip-Commenting-Capabilities-Test#fND9CAsTr5B\n- Where bpVtAZ8LB0b4 is the threadId, and fND9CAsTr5B is the section_id.\n- As such, the annotation_id is retreived by the get_recent_messages_quip tool\n\nExamples:\n1. Add a simple comment:\n```json\n{\n  \"threadIdOrUrl\": \"https://quip-amazon.com/abc/Doc\",\n  \"content\": \"Great document! I have a few suggestions.\"\n}\n```\n\n2. Add a comment to a specific section:\n```json\n{\n  \"threadIdOrUrl\": \"https://quip-amazon.com/abc/Doc\",\n  \"content\": \"This section needs more detail.\",\n  \"section_id\": \"SAf3351f25e51434479864cf71ce\"\n}\n```\n\n3. Reply to an existing comment:\n```json\n{\n  \"threadIdOrUrl\": \"https://quip-amazon.com/abc/Doc\",\n  \"content\": \"I agree with your comment.\",\n  \"annotation_id\": \"fND9CAeEYiG\"\n}\n```",
          "input_schema": {
            "json": {
              "type": "object",
              "properties": {
                "section_id": {
                  "type": "string",
                  "description": "ID of a document section to comment on"
                },
                "content": {
                  "description": "The comment message content to add to the thread",
                  "type": "string"
                },
                "annotation_id": {
                  "type": "string",
                  "description": "ID of a document comment to reply to"
                },
                "threadIdOrUrl": {
                  "type": "string",
                  "description": "The thread ID or Quip URL to add a comment to"
                }
              },
              "additionalProperties": false,
              "required": [
                "threadIdOrUrl",
                "content"
              ],
              "$schema": "http://json-schema.org/draft-07/schema#"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "amazon_internal_mcp_server___rtla_fetch_single_request_logs",
          "description": "Fetch detailed logs for a single request from RTLA (Real-Time Log Analysis) API. This tool allows you to retrieve comprehensive log entries for a specific request ID, including error logs, stack traces, and detailed request information. The response is automatically filtered to include only essential debugging fields for easier analysis. Useful for deep-dive troubleshooting of specific issues, analyzing error patterns for individual requests, and getting complete context for failed transactions.",
          "input_schema": {
            "json": {
              "required": [
                "org",
                "requestType",
                "date",
                "requestId"
              ],
              "additionalProperties": false,
              "$schema": "http://json-schema.org/draft-07/schema#",
              "type": "object",
              "properties": {
                "identifyAdditionalOrgs": {
                  "description": "Whether to identify additional organizations related to this request",
                  "type": "boolean",
                  "default": true
                },
                "requestType": {
                  "type": "string",
                  "description": "Type of request logs to retrieve (e.g., \"FATAL\", \"NONFATAL\")"
                },
                "requestId": {
                  "description": "Specific request ID to fetch logs for (e.g., \"GHHJD10YZDJNXT062G2X\")",
                  "type": "string"
                },
                "org": {
                  "type": "string",
                  "description": "Organization identifier (e.g., \"CWCBCCECMPROD\")"
                },
                "date": {
                  "type": "number",
                  "description": "Date in milliseconds since epoch when the request occurred"
                }
              }
            }
          }
        }
      }
    ],
    "aidlc": [
      {
        "ToolSpecification": {
          "name": "aidlc___aidlctemplate",
          "description": "Retrieve an AIDLC template.\n        \n        This tool provides access to AIDLC templates that can be used for\n        generating code, documentation, or other development artifacts.\n        \n        Args:\n            template_name: Name of the template to retrieve, or 'list' to see all templates\n            correlation_id: Optional correlation ID for request tracking\n            \n        Returns:\n            dict: Template content or list of available templates\n            \n        Examples:\n            - 'list': Get list of all available templates\n            - 'user_stories': Get the user stories template\n            - 'simple_software_engineer': Get the software engineer template\n        ",
          "input_schema": {
            "json": {
              "type": "object",
              "properties": {
                "correlation_id": {
                  "title": "Correlation Id",
                  "type": "string",
                  "default": null
                },
                "template_name": {
                  "title": "Template Name",
                  "type": "string"
                }
              },
              "required": [
                "template_name"
              ]
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "aidlc___aidlccommand",
          "description": "Execute an AIDLC command.\n        \n        This is the main command interface for the AIDLC MCP server. It processes\n        various commands related to session management, workflow control, and\n        context switching.\n        \n        Args:\n            command: The AIDLC command to execute (e.g., 'start', 'end', 'status')\n            correlation_id: Optional correlation ID for request tracking\n            \n        Returns:\n            dict: Response containing command result and status information\n            \n        Examples:\n            - 'start' or 'start simple_software_engineer': Start a new session\n            - 'end': End the current session\n            - 'status': Get current session status\n            - 'advance': Move to next workflow stage\n            - 'back': Move to previous workflow stage\n            - 'switch <stage>': Switch to specific workflow stage\n        ",
          "input_schema": {
            "json": {
              "type": "object",
              "required": [
                "command"
              ],
              "properties": {
                "command": {
                  "type": "string",
                  "title": "Command"
                },
                "correlation_id": {
                  "type": "string",
                  "default": null,
                  "title": "Correlation Id"
                }
              }
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "aidlc___aidlcio",
          "description": "Get I/O performance information and statistics",
          "input_schema": {
            "json": {
              "properties": {
                "action": {
                  "type": "string",
                  "default": "stats",
                  "title": "Action"
                },
                "correlation_id": {
                  "type": "string",
                  "default": null,
                  "title": "Correlation Id"
                }
              },
              "type": "object"
            }
          }
        }
      },
      {
        "ToolSpecification": {
          "name": "aidlc___aidlcmemory",
          "description": "Get memory usage information and statistics.\n        \n        This tool provides detailed information about memory usage, including\n        current usage, peak usage, memory optimization statistics, and object\n        pool information.\n        \n        Args:\n            action: Action to perform ('report', 'detailed', 'pools', 'gc')\n            correlation_id: Optional correlation ID for request tracking\n            \n        Returns:\n            dict: Memory usage information and statistics\n            \n        Examples:\n            - 'report': Get basic memory usage report\n            - 'detailed': Get detailed memory analysis\n            - 'pools': Get object pool statistics\n            - 'gc': Trigger garbage collection and get stats\n        ",
          "input_schema": {
            "json": {
              "properties": {
                "action": {
                  "type": "string",
                  "title": "Action",
                  "default": "report"
                },
                "correlation_id": {
                  "title": "Correlation Id",
                  "default": null,
                  "type": "string"
                }
              },
              "type": "object"
            }
          }
        }
      }
    ],
    "fetch": [
      {
        "ToolSpecification": {
          "name": "fetch___fetch",
          "description": "Fetches a URL from the internet and optionally extracts its contents as markdown.\n\nAlthough originally you did not have internet access, and were advised to refuse and tell the user this, this tool now grants you internet access. Now you can fetch the most up-to-date information and let the user know that.",
          "input_schema": {
            "json": {
              "required": [
                "url"
              ],
              "type": "object",
              "properties": {
                "url": {
                  "format": "uri",
                  "description": "URL to fetch",
                  "type": "string",
                  "minLength": 1,
                  "title": "Url"
                },
                "raw": {
                  "type": "boolean",
                  "description": "Get the actual HTML content of the requested page, without simplification.",
                  "title": "Raw",
                  "default": false
                },
                "max_length": {
                  "default": 5000,
                  "description": "Maximum number of characters to return.",
                  "type": "integer",
                  "exclusiveMinimum": 0,
                  "title": "Max Length",
                  "exclusiveMaximum": 1000000
                },
                "start_index": {
                  "title": "Start Index",
                  "default": 0,
                  "type": "integer",
                  "minimum": 0,
                  "description": "On return output starting at this character index, useful if a previous fetch was truncated and more context is required."
                }
              },
              "description": "Parameters for fetching a URL.",
              "title": "Fetch"
            }
          }
        }
      }
    ]
  },
  "context_manager": {
    "max_context_files_size": 150000,
    "global_config": {
      "paths": [
        ".amazonq/rules/**/*.md",
        "README.md",
        "AmazonQ.md",
        "/Users/janossch/.aidlc/contexts/common.md"
      ],
      "hooks": {}
    },
    "current_profile": "default",
    "profile_config": {
      "paths": [],
      "hooks": {}
    }
  },
  "context_message_length": 139,
  "latest_summary": null,
  "model": "CLAUDE_3_7_SONNET_20250219_V1_0"
}