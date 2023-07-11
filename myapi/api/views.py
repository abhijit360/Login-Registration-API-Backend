from django.http import JsonResponse, HttpResponse
from .models import CustomUser, JWT_storedVal
from .serializers import UserSerializer, UserBankDetailsSerializer, UserUpdateSerializer, UserCreateSerializer ,myUserCreateSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view
import hashlib, datetime
import jwt, json
import traceback


# Create your views here.

JWT_SECRET_KEY = "Fin2Secret"

def displayRoutes(request):
    return JsonResponse({
        "endpoints": {
            1:'getUsers/',
            2:'createUser/',
            3:'loginUser/',
            4:'updateUser/',
            5:'deleteUser/',
            6:'api/token/',
            7:'api/token/refresh/'
        }
    })


def create_JWT(user_id):
    creation_time = datetime.datetime.now(datetime.timezone.utc)
    passed_time = creation_time + datetime.timedelta(minutes=5)
    payload = {
        "id": str(user_id),
        "iat": creation_time,
        'exp': passed_time,
    }
    
    new_secret = JWT_SECRET_KEY + str(user_id)
    encoded_jwt = jwt.encode( payload, new_secret, algorithm="HS256")
    try:
        user_jwt = JWT_storedVal.objects.get(user_id=str(user_id))
        if user_jwt:
            # replaces token in the database
            user_jwt.jwt_token = encoded_jwt
            user_jwt.save()
        
        return encoded_jwt
            # return JsonResponse({'status_code':200,"access_token": encoded_jwt})
    except:
        JWT_storedVal.objects.create(user_id=user_id,jwt_token=encoded_jwt)
        return encoded_jwt

    

def isJWTValid(function):
    def validate(request, *args, **kwargs):
        auth_token = request.headers.get('Authorization',"")
        if not auth_token or not auth_token.startswith('Bearer '):
            return JsonResponse({'status_code':'100','Error':'Missing or Invalid Authorization Token'})
        
        jwt_token = request.headers["Authorization"].split(" ")[1]
        try:
            stored_jwt = JWT_storedVal.objects.get(jwt_token=jwt_token)
            decode = jwt.decode(jwt_token, str(JWT_SECRET_KEY+stored_jwt.user_id), algorithms=['HS256'])
            return function(request, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            return JsonResponse({'status_code':'100','Error':'Expired JWT Token'})
        except jwt.exceptions.InvalidTokenError:
            return JsonResponse({'status_code':'100','Error':'JWT Token Decode Failed (Altered Token)'})
    
    return validate

@api_view(["POST"])
def getFreshJWTToken(request):
    if request.method == "POST":
        email, password = request.data['email'], request.data['password']
        userFound = CustomUser.objects.get(email=email)
        if userFound:
            if str(userFound.password) == str(hashlib.md5(password.encode()).digest()):
                jwt =  create_JWT(userFound.id)
                return JsonResponse({'status_code':200,"access_token":jwt})
            else:
                return JsonResponse({"status_code":100,"Error":"Password Entered is Incorrect"})

        else:
            return JsonResponse({"status_code":100,'Error':"User does not exist"})
     
""" 
redis is like a database. Whenever we create a jwt token, we store the key value pair. 
Key: jwt_token, value:user_id  (inside redis)
At the time of decode, we can pull the user_id from redis as we have the key
Once we have the user_id, we can use the ORM.

Encrypting the payload (Hashing my data)
- pass userid
- standard time
- expiry time
-> don't include any other information
"""

@api_view(["GET"])
@isJWTValid
def testGETendpoint(request):
    return JsonResponse({"message":"only valid with token"})

@api_view(["POST"])
@isJWTValid
def testPOSTendpoint(request):
    val1, val2 = request.data['val1'], request.data['val2']
    return JsonResponse({"message":"only valid with token", 'Val1':val1,"val2":val2})

@api_view(["POST"])
def test_HTTP_response(request):
    response = HttpResponse()
    if request.method =="POST":
        val1 , val2 = request.data['val1'], request.data['val2']
        print(val1+val2)
        jwt = create_JWT(str(val1+val2))
        user_data = CustomUser.objects.get(email="test@email.com")
        serialized_User = UserSerializer(user_data)
        response = HttpResponse(json.dumps(serialized_User.data), content_type="application/json")
        response.headers["Authorization"] = 'Bearer ' + jwt
    return response








"""
When using Response we need to add an @api_view decorator
when entering query params into the url we do it as such: url/?name=abhijit . url/?name="abhijit" is wrong
"""
        

@api_view(["POST"])
def create_user(request):
    if request.method =="POST":
        print("request Data",request.data)
        email_data = [elem['email'] for elem in CustomUser.objects.all().values("email")]
        phone_data = [str(elem['phone']) for elem in CustomUser.objects.all().values("phone")]

        email , phone = request.data["email"] , request.data['phone']
      
        if (email in email_data) or (phone in phone_data):
            return JsonResponse({"Status_code" :"100", "message":"Email or Phone is already linked to an existing Account"})
        
        try:    
            user = myUserCreateSerializer(data=request.data)
            if user.is_valid(raise_exception=True):
    
                created_user = CustomUser.objects.create(name=user.data['name'],email=user.data['email'],phone=user.data['phone'], password=user.data['password'])
        
                serializer = UserSerializer(created_user)

                jwt = create_JWT(created_user.id)
                JsonToReturn = {"status_code":"200", "message":"Successfully Registered","user_data":serializer.data}
                response = HttpResponse(json.dumps(JsonToReturn), content_type="application/json")
                response.headers["authorization"] = 'Bearer ' + jwt
                return response
        except Exception as e:
            return JsonResponse({"Status_code" :"100", "message":f"{e}"})
        

@api_view(["POST"])
def login_user(request):
    if request.method == "POST":
        email, password = request.data["email"], request.data['password']
        try:
            user = CustomUser.objects.get(email=str(email)) # failing
            user.last_login = datetime.datetime.now()
            serializer = UserSerializer(user)
            
            if str(user.password) == str(hashlib.md5(password.encode()).digest()): 
                # we need to convert both of them to strings so that the data type is correct and the comparison is successful
                # this checks the hash value returned with one that we generated from the input password
                jwt = create_JWT(user.id)
                JsonToReturn = {"status_code":"200", "message":"Successfully Logged in","user_data":serializer.data}
                response = HttpResponse(json.dumps(JsonToReturn), content_type="application/json")
                response.headers["Authorization"] = 'Bearer ' + jwt
                return response
        except Exception as e:
            print(e)
            return JsonResponse({"status_code":"100", "message":"Unsucessful login. User does not exist"})
    
        
    
@api_view(['POST'])
@isJWTValid
def update_user(request):
    serialized_data = UserUpdateSerializer(data=request.data)
    if serialized_data.is_valid():
        email = serialized_data.data['email']
        FoundUser = CustomUser.objects.get(email=email)
        if FoundUser:
            FoundUser.email = serialized_data.data['new_email']
            FoundUser.phone = serialized_data.data['phone']
            FoundUser.password = serialized_data.data['password']
            try:
                FoundUser.save()
                serialized_user = UserSerializer(FoundUser)
                return JsonResponse({"status_code":"200", "message":"Successfully Update User", "updated_data": serialized_user.data})
            
            except Exception as e:
                email_data = [elem['email'] for elem in CustomUser.objects.all().values("email")]
                phone_data = [str(elem['phone']) for elem in CustomUser.objects.all().values("phone")]

                phone =  serialized_data.data['phone']
                
                if email in email_data:
                    return JsonResponse({"Status Code": "100", "Error":"Email already registered. Please enter a new Email"})
                if phone in phone_data:
                    return JsonResponse({"Status Code": "100", "Error":"Number is already registered. Please enter a new number"})
                
        else:
            JsonResponse({"status_code":"100", 
                "message":"User does not exist"})

        
@api_view(["POST"])
@isJWTValid
def delete_user(request):
    serialized_user_data = UserUpdateSerializer(data=request.data)
    if serialized_user_data.is_valid():
        FoundUser = CustomUser.objects.get(email=serialized_user_data.data['email'])
        password = serialized_user_data.data['password']
        if str(FoundUser.password)== str(hashlib.md5(password.encode()).digest()):
            FoundUser.delete()
            return JsonResponse({"status_code":"200", 
                    "message":"User Deleted Successfully"})
    
    return JsonResponse({"status_code":"100", 
                "message":"User Deletion Unsuccessful"})

@api_view(["GET"])
@isJWTValid
def get_users(request):
    if request.method == "GET":
        # the query parameters to get filter an user
        name = request.GET.get("name")
        email = request.GET.get('email')
        phone = request.GET.get("phone")  
        display_bank_account = request.GET.get("display_bank_account") == "true" 
        queryset = CustomUser.objects.all()
        serializer_class = UserSerializer

        if  name:
            try:
                # with connection.cursor() as cursor:
                #     cursor.execute("SELECT")
                queryset = queryset.filter(name=name)
            except Exception as e:
                JsonToReturn= {"status_code" :"100", "Message":f"Could not find any user with name: {name} "}
                response = HttpResponse(json.dumps(JsonToReturn), content_type="application/json")
                response.headers["Authorization"] = 'Bearer ' + jwt
                return response

        if email:
            try:
                queryset = queryset.filter(email=email)
                
            except:
                JsonToReturn= {"status_code" :"100", "Message":f"user with email {email} does not exist"}
                response = HttpResponse(json.dumps(JsonToReturn), content_type="application/json")
                response.headers["Authorization"] = 'Bearer ' + jwt
                return response


        if phone:
            try:
                queryset = queryset.filter(phone=int(phone))
            except:
                JsonToReturn = {"status_code" :"100", "Message":f"user with phone number {phone} does not exist"}
                response = HttpResponse(json.dumps(JsonToReturn), content_type="application/json")
                response.headers["Authorization"] = 'Bearer ' + jwt
                return response
        
        if display_bank_account:
            serializer_class = UserBankDetailsSerializer
        
        if len(queryset) > 1:
            serializer = serializer_class(queryset, many=True)
            return Response(serializer.data)

        user_instance = queryset.first()
        serializer = serializer_class(user_instance)

        JsonToReturn= {"status_code" :"200", "data":serializer.data}
        response = HttpResponse(json.dumps(JsonToReturn), content_type="application/json")
        response.headers["Authorization"] = 'Bearer ' + jwt
        return response

            
# @api_view(["Get"])
# @isJWTValid
# def displayUsers(request):
#     qty = request.GET.get('qty')
#     user_id = request.GET.get('user_id')
#     queryset = CustomUser.objects.raw('SELECT * FROM api_User')
    
#     if qty:
#         if int(qty) < len(queryset):
#             queryset = CustomUser.objects.raw(f"SELECT * FROM api_User LIMIT {str(qty)}")
        

#     if user_id:
    
#         user = CustomUser.objects.raw("SELECT * FROM api_User WHERE id=%s",[user_id])
#         if user:
#             print("USER found ------>",user)
#             #return JsonResponse({'name':user.name, 'email':user.email,'phone':user.phone})
#         else:
#             print("no USER FOUND")            
    
#     data = {}
#     for query in queryset:
#         data[query.id] = {'name':query.name, 'email':query.email,'phone':query.phone}

        
#     print(data)
#     return JsonResponse(data)

# @api_view(['POST'])
# def create_updated_user(request):
#     if request.method == "POST":
#         email_data = [elem['email'] for elem in myUser.objects.all().values("email")]
#         phone_data = [str(elem['phone']) for elem in myUser.objects.all().values("phone")]

#         email , phone = request.data["email"] , request.data['phone']
#         if (email in email_data) or (phone in phone_data):
#             return JsonResponse({"Status_code" :"100", "message":"Email or Phone is already linked to an existing Account"})

#         try:
#             myuserData = myUserCreateSerializer(data=request.data)
#             if myuserData.is_valid(raise_exception=True):
#                 myuser = myUser(email=myuserData.data['email'], phone=myuserData.data['phone'],password=myuserData.data['password'])
#                 myuser.first_name = myuserData.data['first_name']
#                 myuser.last_name = myuserData.data['last_name']
#                 myuser.save()

            
#                 return JsonResponse({
#                     "status_code": 200,
#                     "message": "user created",
#                     "user_data": {
#                         'email':myuserData.data['email'],
#                         'phone': myuserData.data['phone'],
#                         'first_name': myuserData.data['first_name'],
#                         'last_name': myuserData.data['last_name']
#                     }
#                 })
#         except Exception as e:
#             print(e)
#             return JsonResponse({
#                 "status_code":100,
#                 'exception':e
#             })


#         email = request.data["email"]
#         phone = request.data["phone"]
#         first_name = request.data["first_name"]
#         last_name = request.data['last_name']
#         password = request.data['password']
#         u     