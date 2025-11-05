#!/usr/bin/env python3
"""
Test runner for EN Learning Pal
Runs all unit tests and reports results
"""
import sys
import unittest


def run_tests():
    """Discover and run all tests"""
    loader = unittest.TestLoader()
    start_dir = 'tests'
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code based on test results
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
