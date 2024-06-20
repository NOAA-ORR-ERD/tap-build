Notes on the example:

yaml file can be made from the Python file with:

```
from tapbuild.utilities import load_config
config = load_config("example_tap-setup.py")
config_d = {key: val for key, val in vars(config).items() if not key.startswith('_')}
yaml.dump(config_d, open("example_tap-setup.yaml",'w'))
```

