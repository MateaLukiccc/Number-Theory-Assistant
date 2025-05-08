import docker
from pathlib import Path
import tempfile

def execute_code_in_docker(code: str) -> dict:
    client = docker.from_env()
    print(code)
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        script_path = tmp_path / "script.py"
        script_path.write_text(code)

        # Run the container using prebuilt image and mount the script
        volumes = {
            str(script_path): {'bind': '/app/script.py', 'mode': 'ro'}
        }

        try:
            output = client.containers.run(
                image="sandbox_runner",
                command=["python", "script.py"],
                volumes=volumes,
                remove=True,
                network_disabled=True,
                mem_limit="100m",
                cpu_period=100000,
                cpu_quota=50000  
            )
            
            return output.decode()
        except docker.errors.ContainerError as e:
            return f"Error: {e.stderr.decode() if e.stderr else str(e)}"
