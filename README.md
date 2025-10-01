# Langflow Desktop Updates

A manifest repository for managing automatic updates of the Langflow desktop application built with Tauri.

## Overview

This repository serves as the update manifest for the Langflow desktop application, providing version information, release notes, and signed binaries for automatic updates across different platforms. The update system follows Tauri's built-in updater specifications, ensuring secure and reliable application updates.

## Project Structure

```
├── latest.json           # Current version manifest
├── releases/            # Release archives organized by version
│   ├── v1.4.21/
│   │   ├── macOS/
│   │   │   └── Langflow.app.tar.gz
│   │   └── windows/
│   │       ├── Langflow_1.4.21_x64_en-US.msi
│   │       └── Langflow_1.4.21_arm64_en-US.msi
│   └── v1.4.2/
│       └── ...
└── README.md
```

## How It Works

### Update Manifest (`latest.json`)

The `latest.json` file contains the current version information and platform-specific download URLs and signatures. The Tauri updater checks this file to determine if a new version is available.

**Supported Platforms:**

- **macOS ARM64** (`darwin-aarch64`): Apple Silicon Macs
- **Windows ARM64** (`windows-aarch64`): ARM-based Windows devices
- **Windows x64** (`windows-x86_64`): Intel/AMD Windows devices

### Security

All releases are cryptographically signed using Tauri's signing mechanism. Each platform entry includes:

- **Signature**: A base64-encoded signature for verifying the authenticity of the download
- **URL**: Direct download link to the release binary
- **Version**: Semantic version number
- **Publication Date**: ISO 8601 timestamp of the release

## Usage

### For Users

The Langflow desktop application automatically checks this repository for updates. When a new version is available, users will be prompted to update through the application's built-in updater.

### For Developers

#### Adding a New Release

1. **Build and sign the application** for all target platforms
2. **Create version directory** in `releases/` (e.g., `releases/v1.4.22/`)
3. **Upload platform binaries** to the appropriate subdirectories:
   - `macOS/` for `.app.tar.gz` files
   - `windows/` for `.msi` files
4. **Update `latest.json`** with:
   - New version number
   - Updated publication date
   - New signatures for each platform
   - Updated download URLs

#### Example `latest.json` Structure

```json
{
  "version": "1.4.21",
  "notes": "Update notes describing changes",
  "pub_date": "2024-03-21T12:00:00Z",
  "platforms": {
    "darwin-aarch64": {
      "signature": "<base64-signature>",
      "url": "https://raw.githubusercontent.com/langflow-ai/desktop-updates/RELEASE/releases/v1.4.21/macOS/Langflow.app.tar.gz"
    },
    "windows-x86_64": {
      "signature": "<base64-signature>",
      "url": "https://media.githubusercontent.com/media/langflow-ai/desktop-updates/RELEASE/releases/v1.4.21/windows/Langflow_1.4.21_x64_en-US.msi"
    }
  }
}
```

## Repository Hosting

This repository is hosted on GitHub and uses:

- **GitHub Raw** for serving the update manifest and macOS binaries
- **GitHub LFS (Large File Storage)** via `media.githubusercontent.com` for Windows MSI files due to their larger size

## Contributing

When contributing new releases:

1. Ensure all binaries are properly signed with the Tauri private key
2. Test the update process in a development environment
3. Verify all download URLs are accessible
4. Update release notes with meaningful change descriptions
5. Follow semantic versioning (SemVer) for version numbers

## Security Considerations

- Never commit private signing keys to this repository
- All signatures should be generated in a secure build environment
- Verify the integrity of uploaded binaries before updating the manifest
- Use HTTPS URLs exclusively for all download links

## Related Links

- [Langflow Desktop Application](https://github.com/langflow-ai/langflow)
- [Tauri Updater Documentation](https://tauri.app/v1/guides/distribution/updater)
- [Semantic Versioning](https://semver.org/)
