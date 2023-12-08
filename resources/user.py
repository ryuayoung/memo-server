from email_validator import EmailNotValidError, validate_email
from flask import request
from flask_jwt_extended import create_access_token
from flask_restful import Resource
from mysql_connection import get_connection

from utils import check_password, hash_password ## 1.
from mysql.connector import Error

class UserRegisterResource(Resource) :

    def post(self) :
        data = request.get_json()

        try :
            validate_email(data['email'])
            
        except EmailNotValidError as e :
            print(e)
            return{ 'error' : str(e) }, 400
        
        if len(data['password']) < 4 or len(data['password']) > 14 :
                return {'error' : '비밀번호 길이가 올바르지 않습니다.'}, 400

        # 비번 암호화       
        password = hash_password(data['password'])

        print(password)

        # DB 에 회원정보 저장한다.
        try :
            Connection = get_connection()
            query = '''insert into user
                    (email, password, nickname)
                    values
                    ( %s, %s, %s );'''
            record = (data['email'],
                      password,
                      data['nickname'])
            
            cursor = Connection.cursor()
            cursor.execute(query, record)
            Connection.commit()

            # 유저 아이디 변수처리하깅 : 회원가입때 필요!
            user_id = cursor.lastrowid

            cursor.close()
            Connection.close()

        except Error as e :
             print(e)
             cursor.close()
             Connection.close()
             return { 'error' : str(e) }, 500
        
        access_token = create_access_token(user_id) # 변수처리 넣기
        
        return { 'result' : 'seccess',
                'accessToken' : access_token }, 200
    

class UserLoginRecource(Resource) :
     
     def post(self) :
          
        data = request.get_json()
         
        try :
            connection = get_connection()

            query = '''select *
                    from user
                    where email = %s;'''
            record = ( data['email'], )

            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)

            result_list = cursor.fetchall()
                    
            cursor.close()
            connection.close()

        except Error as e :
                print(e)
                cursor.close()
                connection.close()
                return {'error' : str(e)}, 500

        if len(result_list) == 0 :
            return {'error' : '회원가입 먼저 하십시오.'}
        
        check = check_password(data['password'] , result_list[0]['password'])

        if check == False :
             return {'error' : '비밀번호가 틀립니다.'} , 400

        access_token = create_access_token(result_list[0]['id'])

        return{'result' : 'success',
               'accessToken' : access_token}, 200
     

     

















