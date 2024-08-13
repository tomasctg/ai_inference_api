import uuid
import time
import hashlib
import platform
import psutil

def generate_chat_id():
    # Generate a random UUID and take the first 8 characters for uniqueness
    unique_part = uuid.uuid4().hex[:8]
    # Construct the chat completion ID
    chat_id = f"chatcmpl-{unique_part}"
    return chat_id

def generate_created_timestamp():
    # Get the current time as a Unix timestamp (in seconds)
    created_timestamp = int(time.time())
    return created_timestamp

def generate_system_fingerprint(model_name, model_version="v3", seed="0"):
    # Concatenate relevant configuration details into a single string
    hardware_details = get_cpu_hardware_details()
    config_string = f"{model_name}-{model_version}-{hardware_details}-{seed}"
    
    # Generate a hash of the configuration string to create the fingerprint
    fingerprint = hashlib.sha256(config_string.encode()).hexdigest()[:12]
    
    # Format it with the "fp_" prefix
    system_fingerprint = f"fp_{fingerprint}"
    
    return system_fingerprint

def get_cpu_hardware_details():
    system = platform.system()
    machine = platform.machine()
    processor = platform.processor()
    return f"{system}-{machine}-{processor}"

def get_detailed_cpu_hardware_details():
    system = platform.system()
    machine = platform.machine()
    processor = platform.processor()
    num_cores = psutil.cpu_count(logical=False)  # Physical cores
    num_threads = psutil.cpu_count(logical=True)  # Logical cores (threads)
    return f"{system}-{machine}-{processor}-cores:{num_cores}-threads:{num_threads}"