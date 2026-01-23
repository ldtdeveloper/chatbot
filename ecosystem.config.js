module.exports = {
  apps: [
    {
      name: 'chatbot-backend',
      script: 'uvicorn',
      args: 'main:app --host 0.0.0.0 --port 8081',
      interpreter: 'mvp/backend/venv/bin/python',
      cwd: '/home/voicequik/app/chatbot/mvp/backend',
      instances: 1,
      exec_mode: 'fork',
      env: {
        PORT: 8081,
        ENVIRONMENT: 'production'
      },
      error_file: '/home/voicequik/app/logs/backend-error.log',
      out_file: '/home/voicequik/app/logs/backend-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G'
    },
    {
      name: 'chatbot-celery',
      script: 'celery',
      args: '-A app.core.celery_app worker --loglevel=info',
      interpreter: 'mvp/backend/venv/bin/python',
      cwd: '/home/voicequik/app/chatbot/mvp/backend',
      instances: 1,
      exec_mode: 'fork',
      env: {
        ENVIRONMENT: 'production'
      },
      error_file: '/home/voicequik/app/logs/celery-error.log',
      out_file: '/home/voicequik/app/logs/celery-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      autorestart: true,
      watch: false
    }
  ]
};
