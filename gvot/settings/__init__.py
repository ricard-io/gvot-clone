import environ

"""The default environment to use."""
DEFAULT_ENVIRONMENT = 'production'

"""The environment variables of the app instance."""
env = environ.Env()

"""Path to the package root - e.g. Django project."""
root_dir = environ.Path(__file__) - 2

"""Path to the base directory of the app instance."""
base_dir = env.path('BASE_DIR', default=str(root_dir - 1))

# Load config.env, OS environment variables will take precedence
if env.bool('READ_CONFIG_FILE', default=True):
    env.read_env(str(base_dir.path('config.env')))

"""The Django settings module's name to use."""
DJANGO_SETTINGS_MODULE = env(
    'DJANGO_SETTINGS_MODULE',
    default='gvot.settings.{}'.format(
        env('ENV', default=DEFAULT_ENVIRONMENT)
    ),
)
