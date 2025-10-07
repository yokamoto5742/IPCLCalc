# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## House Rules:
- 文章ではなくパッチの差分を返す。Return patch diffs, not prose.
- 変更範囲は最小限に抑える。
- コードの修正は直接適用する。
- Pythonコードのimport文は以下の適切な順序に並べ替えてください。
標準ライブラリ
サードパーティライブラリ
カスタムモジュール 
それぞれアルファベット順に並べます。importが先でfromは後です。

# CHANGELOG

このプロジェクトにおけるすべての重要な変更は日本語でCHANGELOG.mdに記録されます。フォーマットは[Keep a Changelog](https://keepachangelog.com/ja/1.1.0/)に基づいています。

## Automatic Notifications (Hooks)
自動通知は`.claude/settings.local.json` で設定済：
- **Stop Hook**: ユーザーがClaude Codeを停止した時に「作業が完了しました」と通知
- **SessionEnd Hook**: セッション終了時に「Claude Code セッションが終了しました」と通知

## Project Overview
IPCLCalc is an OCR-based memo application using Tesseract for Japanese and English text recognition. The app allows users to select a screen region, extract text via OCR, edit the extracted text, and save it to files.

## Architecture
- **Tkinter-based GUI**: Multi-widget modular architecture with separate widgets for control buttons, date selection, diary content, and progress display
- **AI Provider System**: Multi-provider support (Claude, OpenAI, Gemini) with fallback mechanism configured via `utils/config.ini`
- **Configuration Management**: Centralized config via `utils/config_manager.py` handling both `.env` and `config.ini` files
- **Version Management**: Automated version bumping system in `scripts/version_manager.py` that updates `app/__init__.py` and `docs/README.md`

## Key Components
- `main.py`: Entry point (currently minimal/empty)
- `widgets/`: Modular UI components (control_buttons, date_selection, diary_content, progress)
- `utils/config_manager.py`: Config loader with AI provider management (loads .env for API keys, config.ini for settings)
- `utils/env_loader.py`: Environment variable loader
- `scripts/version_manager.py`: Version incrementer (auto-updates version in `app/__init__.py` and README)
- `build.py`: PyInstaller build script (creates "マニュアル検索" executable)

## Development Commands

### Testing
```bash
pytest                    # Run all tests
pytest tests/test_main.py # Run specific test file
pytest --cov             # Run with coverage
```

### Building
```bash
python build.py          # Build executable with PyInstaller (auto-increments version)
```

### Version Management
Version is stored in `app/__init__.py` as `__version__` and `__date__`. Build script automatically increments version.

## Configuration
- **AI Providers**: Set in `utils/config.ini` under `[AI]` section (provider, fallback_provider)
- **API Keys**: Stored in `.env` file (CLAUDE_API_KEY, OPENAI_API_KEY, GEMINI_API_KEY)
- **UI Settings**: Font, window size, calendar colors in `utils/config.ini`
- **Tesseract Path**: Configured via ConfigManager

## Dependencies
Key packages: pytest, pytest-cov, pyinstaller, playwright, python-dotenv, Pygments
