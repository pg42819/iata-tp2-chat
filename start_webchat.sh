
current_dir=$( cd "$( dirname ${BASH_SOURCE[0]} )" && pwd )
source "$current_dir/venv/bin/activate" 

export PYTHONPATH=${current_Dir}:${PYTHONPATH}
export FLASK_APP=webchat.py
FLASK_ENV=development
FLASK_DEBUG=1
python -m flask run
