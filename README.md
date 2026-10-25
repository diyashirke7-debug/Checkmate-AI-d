# Checkmate AI — Chess Endgame Assistant

A Flask chess website with a custom Minimax AI and alpha-beta pruning. The `python-chess` library handles chess rules; our `minimax.py` implements the AI decision-making.

## Run on Windows

1. Install Python 3.11 or newer.
2. Extract the ZIP and open the folder in VS Code.
3. Open the terminal in the project folder and run:

```powershell
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

4. Open http://127.0.0.1:5000

## Notes

- Easy, Normal, and Hard use search depths 1, 2, and 3. Higher depth may take longer.
- This is a learning project, not a tournament-strength chess engine.
- Set a strong `SECRET_KEY` before deployment.
- The included in-memory game store is intended for local demonstration. Production multi-worker hosting should use a proper session/game store.
