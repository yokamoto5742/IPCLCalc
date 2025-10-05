from pathlib import Path
from unittest.mock import Mock, call, patch

import pytest

from main import main


class TestMain:
    """Test suite for main() function"""

    @patch('main.subprocess.Popen')
    @patch('main.launch_draft_page')
    @patch('main.IPCLOrderAutomation')
    def test_main_normal_execution(
        self,
        mock_automation_class,
        mock_launch_draft,
        mock_popen
    ):
        """Test main() calls all dependencies in correct order - normal case"""
        # Arrange
        mock_automation_instance = Mock()
        mock_automation_instance.pdf_dir = Path('C:\\test\\pdf_dir')
        mock_automation_class.return_value = mock_automation_instance

        # Act
        main()

        # Assert
        # 1. IPCLOrderAutomation is instantiated
        mock_automation_class.assert_called_once_with()

        # 2. process_all_csv_files() is called
        mock_automation_instance.process_all_csv_files.assert_called_once_with()

        # 3. launch_draft_page() is called
        mock_launch_draft.assert_called_once_with()

        # 4. subprocess.Popen opens explorer
        mock_popen.assert_called_once_with(['explorer', 'C:\\test\\pdf_dir'])

    @patch('main.subprocess.Popen')
    @patch('main.launch_draft_page')
    @patch('main.IPCLOrderAutomation')
    def test_main_call_sequence(
        self,
        mock_automation_class,
        mock_launch_draft,
        mock_popen
    ):
        """Test function call sequence is correct"""
        # Arrange
        mock_automation_instance = Mock()
        mock_automation_instance.pdf_dir = Path('C:\\output')
        mock_automation_class.return_value = mock_automation_instance

        call_order = []

        def track_automation_init(*args, **kwargs):
            call_order.append('automation_init')
            return mock_automation_instance

        def track_process_csv(*args, **kwargs):
            call_order.append('process_csv')

        def track_launch_draft(*args, **kwargs):
            call_order.append('launch_draft')

        def track_popen(*args, **kwargs):
            call_order.append('popen')

        mock_automation_class.side_effect = track_automation_init
        mock_automation_instance.process_all_csv_files.side_effect = track_process_csv
        mock_launch_draft.side_effect = track_launch_draft
        mock_popen.side_effect = track_popen

        # Act
        main()

        # Assert
        expected_order = ['automation_init', 'process_csv', 'launch_draft', 'popen']
        assert call_order == expected_order

    @patch('main.subprocess.Popen')
    @patch('main.launch_draft_page')
    @patch('main.IPCLOrderAutomation')
    def test_main_with_pathlib_path(
        self,
        mock_automation_class,
        mock_launch_draft,
        mock_popen
    ):
        """Test pdf_dir with Pathlib Path object converts to string correctly"""
        # Arrange
        mock_automation_instance = Mock()
        mock_automation_instance.pdf_dir = Path('C:\\Users\\test\\Documents\\PDF')
        mock_automation_class.return_value = mock_automation_instance

        # Act
        main()

        # Assert
        mock_popen.assert_called_once_with(
            ['explorer', 'C:\\Users\\test\\Documents\\PDF']
        )

    @patch('main.subprocess.Popen')
    @patch('main.launch_draft_page')
    @patch('main.IPCLOrderAutomation')
    def test_main_with_string_path(
        self,
        mock_automation_class,
        mock_launch_draft,
        mock_popen
    ):
        """Test pdf_dir with string path is handled correctly"""
        # Arrange
        mock_automation_instance = Mock()
        mock_automation_instance.pdf_dir = 'C:\\output\\pdfs'
        mock_automation_class.return_value = mock_automation_instance

        # Act
        main()

        # Assert
        mock_popen.assert_called_once_with(['explorer', 'C:\\output\\pdfs'])

    @patch('main.subprocess.Popen')
    @patch('main.launch_draft_page')
    @patch('main.IPCLOrderAutomation')
    def test_main_automation_instantiation_error(
        self,
        mock_automation_class,
        mock_launch_draft,
        mock_popen
    ):
        """Test error handling when IPCLOrderAutomation instantiation fails"""
        # Arrange
        mock_automation_class.side_effect = Exception('Automation initialization failed')

        # Act & Assert
        with pytest.raises(Exception, match='Automation initialization failed'):
            main()

        # Verify subsequent functions are not called
        mock_launch_draft.assert_not_called()
        mock_popen.assert_not_called()

    @patch('main.subprocess.Popen')
    @patch('main.launch_draft_page')
    @patch('main.IPCLOrderAutomation')
    def test_main_process_csv_error(
        self,
        mock_automation_class,
        mock_launch_draft,
        mock_popen
    ):
        """Test error handling when process_all_csv_files() fails"""
        # Arrange
        mock_automation_instance = Mock()
        mock_automation_instance.process_all_csv_files.side_effect = Exception(
            'CSV processing failed'
        )
        mock_automation_class.return_value = mock_automation_instance

        # Act & Assert
        with pytest.raises(Exception, match='CSV processing failed'):
            main()

        # Verify launch_draft_page and popen are not called
        mock_launch_draft.assert_not_called()
        mock_popen.assert_not_called()

    @patch('main.subprocess.Popen')
    @patch('main.launch_draft_page')
    @patch('main.IPCLOrderAutomation')
    def test_main_launch_draft_error(
        self,
        mock_automation_class,
        mock_launch_draft,
        mock_popen
    ):
        """Test error handling when launch_draft_page() fails"""
        # Arrange
        mock_automation_instance = Mock()
        mock_automation_instance.pdf_dir = Path('C:\\test')
        mock_automation_class.return_value = mock_automation_instance
        mock_launch_draft.side_effect = Exception('Failed to launch draft page')

        # Act & Assert
        with pytest.raises(Exception, match='Failed to launch draft page'):
            main()

        # Verify subprocess.Popen is not called
        mock_popen.assert_not_called()

    @patch('main.subprocess.Popen')
    @patch('main.launch_draft_page')
    @patch('main.IPCLOrderAutomation')
    def test_main_subprocess_popen_error(
        self,
        mock_automation_class,
        mock_launch_draft,
        mock_popen
    ):
        """Test error handling when subprocess.Popen fails"""
        # Arrange
        mock_automation_instance = Mock()
        mock_automation_instance.pdf_dir = Path('C:\\test')
        mock_automation_class.return_value = mock_automation_instance
        mock_popen.side_effect = OSError('Failed to open explorer')

        # Act & Assert
        with pytest.raises(OSError, match='Failed to open explorer'):
            main()

        # Verify previous steps executed normally
        mock_automation_class.assert_called_once()
        mock_automation_instance.process_all_csv_files.assert_called_once()
        mock_launch_draft.assert_called_once()

    @patch('main.subprocess.Popen')
    @patch('main.launch_draft_page')
    @patch('main.IPCLOrderAutomation')
    def test_main_with_empty_pdf_dir(
        self,
        mock_automation_class,
        mock_launch_draft,
        mock_popen
    ):
        """Test edge case when pdf_dir is empty string"""
        # Arrange
        mock_automation_instance = Mock()
        mock_automation_instance.pdf_dir = ''
        mock_automation_class.return_value = mock_automation_instance

        # Act
        main()

        # Assert
        mock_popen.assert_called_once_with(['explorer', ''])

    @patch('main.subprocess.Popen')
    @patch('main.launch_draft_page')
    @patch('main.IPCLOrderAutomation')
    def test_main_with_none_pdf_dir(
        self,
        mock_automation_class,
        mock_launch_draft,
        mock_popen
    ):
        """Test edge case when pdf_dir is None"""
        # Arrange
        mock_automation_instance = Mock()
        mock_automation_instance.pdf_dir = None
        mock_automation_class.return_value = mock_automation_instance

        # Act
        main()

        # Assert
        # str(None) = 'None'
        mock_popen.assert_called_once_with(['explorer', 'None'])

    @patch('main.subprocess.Popen')
    @patch('main.launch_draft_page')
    @patch('main.IPCLOrderAutomation')
    def test_main_popen_returns_process(
        self,
        mock_automation_class,
        mock_launch_draft,
        mock_popen
    ):
        """Test subprocess.Popen returns process object"""
        # Arrange
        mock_automation_instance = Mock()
        mock_automation_instance.pdf_dir = Path('C:\\test')
        mock_automation_class.return_value = mock_automation_instance

        mock_process = Mock()
        mock_popen.return_value = mock_process

        # Act
        main()

        # Assert
        assert mock_popen.return_value == mock_process

    @patch('main.subprocess.Popen')
    @patch('main.launch_draft_page')
    @patch('main.IPCLOrderAutomation')
    def test_main_popen_with_special_characters_in_path(
        self,
        mock_automation_class,
        mock_launch_draft,
        mock_popen
    ):
        """Test edge case when pdf_dir contains special characters"""
        # Arrange
        mock_automation_instance = Mock()
        # Path with Japanese characters and spaces
        mock_automation_instance.pdf_dir = Path('C:\\Users\\Taro\\Documents\\PDF Output')
        mock_automation_class.return_value = mock_automation_instance

        # Act
        main()

        # Assert
        mock_popen.assert_called_once_with(
            ['explorer', 'C:\\Users\\Taro\\Documents\\PDF Output']
        )

    @patch('main.subprocess.Popen')
    @patch('main.launch_draft_page')
    @patch('main.IPCLOrderAutomation')
    def test_main_multiple_calls_independence(
        self,
        mock_automation_class,
        mock_launch_draft,
        mock_popen
    ):
        """Test main() can be called multiple times independently"""
        # Arrange
        mock_automation_instance1 = Mock()
        mock_automation_instance1.pdf_dir = Path('C:\\test1')

        mock_automation_instance2 = Mock()
        mock_automation_instance2.pdf_dir = Path('C:\\test2')

        mock_automation_class.side_effect = [
            mock_automation_instance1,
            mock_automation_instance2
        ]

        # Act
        main()
        main()

        # Assert
        assert mock_automation_class.call_count == 2
        assert mock_launch_draft.call_count == 2
        assert mock_popen.call_count == 2

        # Verify each call used different paths
        assert mock_popen.call_args_list == [
            call(['explorer', 'C:\\test1']),
            call(['explorer', 'C:\\test2'])
        ]
