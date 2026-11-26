"""Create and inspect a local synthetic single-file Relate store."""
import argparse
import json
from pathlib import Path
import relate
from graph import seed
from intelligence import graph_counts
from network import network

def create_store(path):
    path=Path(path)
    if path.suffix!=".rl" or path.exists():
        raise ValueError("Choose a new .rl file; existing files are never overwritten.")
    path.parent.mkdir(parents=True,exist_ok=True)
    db=relate.connect(str(path))
    try:
        seed(db)
        db.commit()
    finally:
        db.close()
    return inspect_store(path)

def inspect_store(path):
    path=Path(path)
    if not path.is_file() or path.suffix!=".rl":
        raise ValueError("Existing .rl file required.")
    db=relate.connect(str(path),read_only=True)
    try:
        nodes,edges=graph_counts(db)
        return {"nodes":nodes,"edges":edges}
    finally:
        db.close()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("command",choices=["create","inspect","export"])
    p.add_argument("path",type=Path)
    a=p.parse_args()
    if a.command=="create":
        result=create_store(a.path)
    elif a.command=="inspect":
        result=inspect_store(a.path)
    else:
        if not a.path.is_file() or a.path.suffix!=".rl":
            p.error("Existing .rl file required.")
        db=relate.connect(str(a.path),read_only=True)
        try: result=network(db)
        finally: db.close()
    print(json.dumps(result,indent=2))

if __name__=="__main__":
    main()
