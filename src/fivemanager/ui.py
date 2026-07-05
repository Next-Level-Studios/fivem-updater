from rich.console import Console

console = Console()


def info(message: str) -> None:
    console.print(f"[cyan]•[/] {message}")


def success(message: str) -> None:
    console.print(f"[green]✓[/] {message}")


def warn(message: str) -> None:
    console.print(f"[yellow]![/] {message}")


def error(message: str) -> None:
    console.print(f"[red]✗[/] {message}")
