# -*- coding: utf-8 -*-
"""
🧪 Test Git Updater - Script de testare rapidă
Verifică funcționalitatea Git Updater înainte de build
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path

def test_git_commands():
    """Testează comenzile git de bază"""
    print("🧪 Testing git commands...")
    
    commands = [
        "git --version",
        "git status --porcelain", 
        "git branch --show-current",
        "git remote -v"
    ]
    
    results = {}
    for cmd in commands:
        try:
            result = subprocess.run(
                cmd, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            results[cmd] = {
                "success": result.returncode == 0,
                "output": result.stdout.strip(),
                "error": result.stderr.strip()
            }
            
            status = "✅" if results[cmd]["success"] else "❌"
            print(f"   {status} {cmd}")
            
        except subprocess.TimeoutExpired:
            results[cmd] = {"success": False, "error": "Timeout"}
            print(f"   ⏱️ {cmd} - Timeout")
        except Exception as e:
            results[cmd] = {"success": False, "error": str(e)}
            print(f"   💥 {cmd} - Error: {e}")
    
    return results

def test_git_updater_import():
    """Testează importul Git Updater"""
    print("\n🧪 Testing Git Updater import...")
    
    try:
        # Add current directory to path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        # Try importing
        import git_updater
        print("   ✅ Git Updater import successful")
        
        # Test class instantiation
        updater = git_updater.GitUpdater()
        print("   ✅ GitUpdater class instantiation successful")
        
        # Test basic properties 
        print(f"   📁 Repository path: {updater.repo_path}")
        print(f"   🔧 Update status: {updater.is_updating}")
        
        # Cleanup
        updater.root.destroy()
        print("   ✅ Cleanup successful")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"   💥 Unexpected error: {e}")
        return False

def test_build_script():
    """Testează prezența și validitatea build script-ului"""
    print("\n🧪 Testing build script...")
    
    build_script = "build_updater.py"
    if os.path.exists(build_script):
        print(f"   ✅ {build_script} exists")
        
        try:
            with open(build_script, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for essential components
            checks = [
                ("PyInstaller", "pyinstaller" in content.lower()),
                ("Spec file creation", "create_spec_file" in content),
                ("Build function", "def build_exe" in content),
                ("Main function", "if __name__ == \"__main__\"" in content)
            ]
            
            for check_name, condition in checks:
                status = "✅" if condition else "❌"
                print(f"   {status} {check_name}")
            
            return all(condition for _, condition in checks)
            
        except Exception as e:
            print(f"   💥 Error reading build script: {e}")
            return False
    else:
        print(f"   ❌ {build_script} not found")
        return False

def test_paths_and_dependencies():
    """Testează paths și dependențele necesare"""
    print("\n🧪 Testing paths and dependencies...")
    
    # Check Python executable
    python_exe = sys.executable
    print(f"   ✅ Python executable: {python_exe}")
    
    # Check tkinter availability  
    try:
        import tkinter as tk
        root = tk.Tk()
        root.destroy()
        print("   ✅ Tkinter available and working")
    except Exception as e:
        print(f"   ❌ Tkinter error: {e}")
        return False
    
    # Check current directory structure
    current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    
    expected_files = [
        "git_updater.py",
        "build_updater.py", 
        "BUILD_UPDATER.bat"
    ]
    
    for file_name in expected_files:
        file_path = current_dir / file_name
        status = "✅" if file_path.exists() else "❌"
        print(f"   {status} {file_name}")
    
    # Check if it's a git repository
    git_dir = current_dir / ".git"
    status = "✅" if git_dir.exists() else "❌"
    print(f"   {status} Git repository (.git folder)")
    
    return True

def test_executable_detection():
    """Testează detectarea aplicației principale"""
    print("\n🧪 Testing main application detection...")
    
    current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    
    # Check for main application files
    main_files = [
        ("punctaj.py", "Main Python script"),
        ("dist/Punctaj.exe", "Main executable"),
        ("Punctaj.exe", "Executable in root")
    ]
    
    found_any = False
    for file_path, description in main_files:
        full_path = current_dir / file_path
        if full_path.exists():
            print(f"   ✅ {description}: {full_path}")
            found_any = True
        else:
            print(f"   ⚪ {description}: Not found")
    
    if found_any:
        print("   ✅ At least one main application found")
    else:
        print("   ⚠️ No main application found - restart feature may not work")
    
    return True

def run_all_tests():
    """Rulează toate testele"""
    print("=" * 60)
    print("🧪 GIT UPDATER TESTING SUITE")
    print("=" * 60)
    
    tests = [
        ("Git Commands", test_git_commands),
        ("Git Updater Import", test_git_updater_import),
        ("Build Script", test_build_script),
        ("Paths & Dependencies", test_paths_and_dependencies),
        ("Executable Detection", test_executable_detection)
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\n🔬 Running {test_name}...")
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"   💥 Test failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, result in results.items():
        if isinstance(result, bool):
            status = "✅ PASS" if result else "❌ FAIL"
            if result:
                passed += 1
            else:
                failed += 1
        else:
            status = "🔍 INFO"
        
        print(f"{status} {test_name}")
    
    # Overall result
    print("\n" + "=" * 60)
    if failed == 0:
        print("🎉 ALL TESTS PASSED - Git Updater is ready to build!")
        print("▶️  Run: BUILD_UPDATER.bat or python build_updater.py")
    else:
        print(f"⚠️ {failed} test(s) failed - Fix issues before building")
        print("📋 Check the error messages above for details")
    
    print("=" * 60)
    
    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    
    print(f"\n🏁 Testing completed. Result: {'SUCCESS' if success else 'FAILURE'}")
    
    # Wait for user input in interactive mode
    try:
        input("\nPress ENTER to exit...")
    except:
        pass
    
    sys.exit(0 if success else 1)