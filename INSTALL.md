# Installation Guide for TransferX

## Introduction

TransferX is a powerful email management and file transfer platform built with Flask. This guide will walk you through the installation process step by step.

## System Requirements

### Minimum Requirements
- **Python**: 3.8 or higher
- **Database**: SQLite (default), PostgreSQL, or MySQL
- **RAM**: 512 MB minimum, 1 GB recommended
- **Storage**: 100 MB for application + additional space for uploads
- **OS**: Linux, macOS, or Windows

### Recommended Requirements
- **Python**: 3.10 or higher
- **Database**: PostgreSQL 12+
- **RAM**: 2 GB or more
- **Storage**: 1 GB+ for uploads
- **OS**: Ubuntu 20.04 LTS or equivalent

### Dependencies
All Python dependencies are listed in `requirements.txt` and will be installed automatically.

## Python Installation

### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv -y