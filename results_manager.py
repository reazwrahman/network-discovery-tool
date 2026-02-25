import os
import json
from datetime import datetime


def get_results_dir():
    """Ensure results directory exists and return its path."""
    results_dir = os.path.join(os.path.dirname(__file__), "results")
    os.makedirs(results_dir, exist_ok=True)
    return results_dir


def get_session_filename():
    """Generate a timestamped results filename for this session."""
    return os.path.join(get_results_dir(), f"results.json")


def initialize_results_file(filename, interface):
    """Create a new results file with session metadata and initial interface info."""
    data = {
        "session_timestamp": datetime.now().isoformat(),
        "selected_interface": interface,
        "scan_results": []
    }
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Results will be saved to: {filename}")


def append_result(filename, discovery_type, hosts):
    """Append a discovery result to the results file."""
    with open(filename, "r") as f:
        data = json.load(f)
    
    result = {
        "timestamp": datetime.now().isoformat(),
        "discovery_type": discovery_type,
        "hosts": hosts
    }
    data["scan_results"].append(result)
    
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
