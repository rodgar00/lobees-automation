# Automatización Django + n8n para Lobees

## Arquitectura

Este proyecto combina **Django** como backend y **n8n** como motor de automatización para la gestión de formularios y sincronización con la API de **Lobees**.  

- **Django:**  
  - Gestiona los datos de los usuarios y sus respuestas a los formularios.  
  - Genera y guarda los `taskid` para cada flujo de tarea.  
  - Envía emails mediante el endpoint `send_form_email`.  
  - Sobrescribe los campos de los formularios 1, 2 y 3 en un único registro por usuario.  

- **n8n:**  
  - Orquesta la ejecución periódica de tareas.  
  - Obtiene los tasks pendientes de la API de Lobees.  
  - Filtra, elimina duplicados y envía datos al endpoint Django para disparar los emails.  
  - Registra las respuestas de cada formulario y actualiza el estado de las tareas en Lobees.  

---

## Workflow Logic

1. **Disparo periódico:**  
   - n8n ejecuta un workflow cada minuto mediante un **Schedule Trigger**.  

2. **Obtención de tasks:**  
   - HTTP Request a Lobees:
     ```
     GET https://api.lobees.com/api/automationtaskschedule/proactive?email=EMAIL
     ```  
   - Saca el data necesario, filtra tareas pendientes (`status` pendiente) y elimina duplicados.  

3. **Envío de emails:**  
   - HTTP Request a Django:
     ```
     POST https://baleless-otha-soaked.ngrok-free.dev/form/send-form-email/
     ```
   - Body:
     ```json
     {
       "lead_email": "usuario@example.com",
       "step": 1,
       "taskid": "id_task"
     }
     ```

4. **Gestión de formularios en Django:**  
   - Django sobrescribe los campos de cada formulario en un único registro.  
   - Ejemplo de función que recibe la respuesta de un formulario:
     ```python
     @csrf_exempt
     def submit_step1(request, lead_email):
         obj = get_or_create_lead(lead_email)
         serializer = Step1Serializer(data=request.POST)
         serializer.is_valid(raise_exception=True)

         for k, v in serializer.validated_data.items():
             setattr(obj, k, v)

         obj.current_step = 1
         obj.save()

         payload = {
             "lead_email": lead_email,
             "step": 1,
             "status": "pending",
             "data": serializer.validated_data,
             "taskid": obj.taskid
         }

         send_to_n8n(N8N_WEBHOOK_FORM1, payload)
         send_email(lead_email, 2)

         return JsonResponse({"ok": True, "next_step": 2, "taskid": obj.taskid})
     ```

5. **Registro de logs y actualización de estado en Lobees:**  
   - Una vez el usuario responde, n8n envía un log, dependiendo de la respuesta que haya sido del step que toque:
     ```json
     POST https://api.lobees.com/api/project/addtasklog?token=TOKEN
     {
       "taskid": "id_task",
       "description": {
         "interested": true,
         "reschedule": true,
         "preferred_date": null
       }
     }
     ```
   - Luego actualiza el estado de la tarea a completada:
     ```
     POST https://api.lobees.com/api/automationtaskschedule/webhook/n8n/callback
     ```

---

## API Endpoints

### Django Endpoints

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/form/send-form-email/` | POST | Envía un email al usuario con el enlace al formulario correspondiente. |
| `/form/step1/<lead_email>/` | GET | Renderiza el formulario 1 para el usuario. |
| `/form/step1/<lead_email>/submit/` | POST | Recibe la respuesta del formulario 1 y la guarda en Django. |
| `/form/step2/<lead_email>/` | GET | Renderiza el formulario 2. |
| `/form/step2/<lead_email>/submit/` | POST | Recibe la respuesta del formulario 2. |
| `/form/step3/<lead_email>/` | GET | Renderiza el formulario 3. |
| `/form/step3/<lead_email>/submit/` | POST | Recibe la respuesta del formulario 3. |
| `/pending-leads/` | GET | Lista todos los leads que no han completado los tres formularios. |

### Lobees Endpoints

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `https://api.lobees.com/api/automationtaskschedule/proactive?email=EMAIL` | GET | Obtiene los tasks pendientes del usuario. |
| `https://api.lobees.com/api/project/addtasklog?token=TOKEN` | POST | Añade un log con la respuesta del formulario al task correspondiente. |
| `https://api.lobees.com/api/automationtaskschedule/webhook/n8n/callback` | POST | Cambia el estado de la tarea a completado (`status = 3`). |

---

## How to Run the System

1. **Django Backend:**  
   ```bash
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py runserver
