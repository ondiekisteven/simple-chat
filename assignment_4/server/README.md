# CHAT SERVER

### Files in directory

- `chatserver.py` - The server program. Is invoked as:
  

    ./chatserver <port>

  
- `users_data.json` - Is our database. It is a json file in this format: 
```json
{
  "user": {
    "username": "user",
    "password": null,
    "step": 0,
    "authenticated": false,
    "app": null
  }
}
```

