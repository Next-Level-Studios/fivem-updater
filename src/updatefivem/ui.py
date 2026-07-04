from rich.console import Console

console = Console()


def success(message: str) -> None:
    console.print(f"[bold green]✓[/] {message}")


def info(message: str) -> None:
    console.print(f"[bold blue]•[/] {message}")


def warn(message: str) -> None:
    console.print(f"[bold yellow]![/] {message}")


def error(message: str) -> None:
    console.print(f"[bold red]✗[/] {message}")
