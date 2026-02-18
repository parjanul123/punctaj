# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('D:\\punctaj\\discord_config.ini', '.'), ('D:\\punctaj\\supabase_config.ini', '.')]
binaries = []
hiddenimports = ['BANK_INTEGRATION_EXAMPLE', 'CAPTURE_EXE_LOG', 'CHECK_EXE_FILES', 'CHECK_LOCAL_JSON', 'CHECK_SUPERUSER', 'DATABASE_CONNECTION_DIAGNOSTIC', 'DEPLOY_EXE_TO_ROOT', 'FINAL_FIX_VERIFICATION', 'FIX_DUPLICATE_LOGS', 'FIX_REALTIME_SYNC_COMPLETE', 'INIT_USERS_JSON', 'INTEGRATION_ENHANCED_ADMIN', 'INTEGRATION_EXAMPLE', 'MULTIDEVICE_AUTH_FIX', 'PACKAGE_FOR_DISTRIBUTION', 'QUICK_BUILD', 'QUICK_TEST_DATABASE', 'RESET_LOGGING_INFO', 'RUN_ALL_DIAGNOSTICS', 'action_logger', 'add_column', 'add_supabase_columns', 'add_user_dialog', 'admin_panel', 'admin_permissions', 'admin_ui', 'backup_manager', 'bank_api_manager', 'bank_transactions', 'bt_api', 'build_exe', 'build_installer_final', 'check_all_tables_sync', 'check_and_sync_discord_users', 'check_audit_logs', 'check_column', 'check_rls_status', 'check_table_structure', 'check_tables', 'clean_and_sync_employees', 'clean_local_duplicates', 'clean_supabase_duplicates', 'clear_all_logs', 'cloud_data_sync_manager', 'cloud_sync_manager', 'config_loader_robust', 'config_resolver', 'create_action_logs_table', 'create_installer', 'create_installer_exe', 'create_installer_v2', 'create_normalized_tables', 'create_tables_auto', 'data_directory_manager', 'debug_sync_connection', 'delete_all_logs_supabase', 'delete_test_logs', 'diagnose_realtime_sync', 'diagnose_valentine_sync', 'diagnostic_logging', 'diagnostic_save_issues', 'disable_rls_for_testing', 'discord_auth', 'discord_auth_test', 'discord_setup_wizard', 'employee_display', 'enhanced_admin_permissions', 'generate_test_log', 'global_hierarchy_admin_panel', 'global_hierarchy_permissions', 'initialize_supabase_tables', 'insert_test_logs', 'inspect_discord_users', 'installer_app', 'installer_gui', 'institution_permissions', 'json_encryptor', 'list_supabase_tables', 'monitor_realtime_sync', 'monthly_report_scheduler', 'multi_device_sync_manager', 'notification_system', 'oauth_callback_server', 'organization_view', 'permission_check_helpers', 'permission_decorators', 'permission_sync_fix', 'populate_employees_tables', 'realtime_sync', 'revolut_api', 'setup_action_logs_table', 'setup_installer_folder', 'setup_permissions_tool', 'show_employees_in_table', 'supabase_employee_manager', 'supabase_realtime_ws', 'supabase_sync', 'sync_all_cities_institutions', 'sync_data_to_supabase', 'sync_employees_to_supabase', 'sync_final', 'sync_saint_denis', 'test_action_logger_real', 'test_action_logging', 'test_action_monitoring', 'test_admin_panel', 'test_and_verify', 'test_bank_integration', 'test_bidirectional_sync', 'test_button_permissions', 'test_cloud_sync', 'test_deduplication_system', 'test_detailed_institution_logging', 'test_detailed_logging', 'test_detailed_logging_new', 'test_institutions_dropdown', 'test_local_logging', 'test_logging_structure', 'test_logs_button', 'test_logs_ui', 'test_no_false_edits', 'test_permissions', 'test_reset_fix', 'test_reset_logging', 'test_save_institution_logging', 'test_save_permissions', 'test_supabase_logging', 'test_sync_flow', 'update_user_role', 'upload_permission_validator', 'users_permissions_json_manager']
tmp_ret = collect_all('tkinter')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('requests')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('websockets')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['..\\punctaj.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Punctaj',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='Punctaj',
)
