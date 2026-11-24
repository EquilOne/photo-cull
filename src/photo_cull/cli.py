import argparse

parser = argparse.ArgumentParser(
    prog="photo-cull",
    description="A cli photo culling application with llm and decision model escalation.",
)
args = parser.parse_args()


def main():
    parser.print_help()
