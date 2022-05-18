import cv2
import numpy as np
import time
import mysql.connector
import datetime


def empty(a):
    pass


#cv2.namedWindow('CAM')
#cv2.createTrackbar('Threshold1','CAM',47,255,empty)
#cv2.createTrackbar('Threshold2','CAM',30,255,empty)



def escreveDb():
    
    try:
        mydb = mysql.connector.connect(
            host ="10.3.12.236",
            user ="PBI_SL",
            password ="$NMeng1376@",
            db = "Processo_Refri")

    
        cursor = mydb.cursor()
        cursor.execute("INSERT INTO TB_CONTA_BAG VALUES (ADDDATE(now(), INTERVAL -3 HOUR), null)")

        mydb.commit()
    
    except mysql.connector.Error as err:
        with open('LogErros.txt', 'a') as f:
            f.write(f"Error Code:  {err.errno}\n")
            f.write(f"SQLSTATE:  {err.sqlstate}\n")
            f.write(f"Message: {err.msg}\n")
            f.write(f"Hora : {time.strftime('%d/%m/%Y %H:%M:%S')}\n\n")



def elapseTime(inicio,fim):
    return fim-inicio



#função chamada no codigo recebendo a região de interesse com o tratamento e a imagem original
def getContours(img, imgContour):
    #primeiro imagem a ser analisada
    #tipo de detecção  do contorno
    #tipo de aproximação do contorno
    _,contours,hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # w,h = 0,0
    # for cnt in contours:
        # area = cv2.contourArea(cnt)            
        # if area>=25000:
            #primeiro parametro imagem a ser desenhada
            #segunda coordenadas de contorno
            #terceiro condição para exibição de contorno
            #quarto cor do contorno
            #expessura do contorno
            #cv2.drawContours(imgContour[210:1080,450:1920], cnt, -1, (255,0,255),3)
            # peri = cv2.arcLength(cnt,True)
            # approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
            # x,y,w,h = cv2.boundingRect(approx)
            
    return contours


#Local onde é defino a câmera que irá ser capturado o frame
#também é possível passar um arquivo no lugar do índice
#o retorno dessa função é uma stream
vid = cv2.VideoCapture("E:\Cursos\BootCamp's\FullStack IGTI\Bootcamp_FullStack_IGTI\FrontEnd com React\Aula 06 - Class Components – Parte 2\Aula 6.1 - Class Components.mp4")


#seta largura e altura do frame onde 3 é a largura e 4 a altura
vid.set(3,1920)
vid.set(4,1080)


#definição de variáveis do código
startTime = 0
endTime = 0
awaitTime = 0
saiu = 0

#loop infinito
while True:
    #print(f'Tempo (contando -, fora +): {round(elapseTime(startTime,endTime),0)}')

    #função onde tenho como retorno o ret = exito na leitura da stream, e frame a própria tela
    ret,frame = vid.read()

    #define quais pixels do frame seram utilizados
    editedf = frame[0:1080,0:1920]

    #mudando o espectro de cores da imagem de BGR para HSV
    edited = cv2.cvtColor(editedf,cv2.COLOR_BGR2HSV)

    #definindo o tamanho da imagem e passando para o roi
    roi = edited[210:500,450:680]
    #cv2.rectangle(editedf,(450,210),(680,500), (0,0,255),3)
    
    #definindo qual dimensão do HSV eu estou utilizando (':,:' refere-se ao tamanho total da imagem) e o indicie 1 refere-se à dimensão a ser utilizada
    cannyRoi = roi[:,:,1]

    #passando a imagem por um filtro de suavização onde é passado a imagem a ser suavizada, e a matriz a ser utilizada para a convolução
    #o ultimo parâmetro passado seria para aplicação de um desvio padrão na direção X, no caso o valor zero representa que esse desvio não será utilizado
    cannyRoi = cv2.GaussianBlur(cannyRoi,(1,1),0)


    #Area1 = cv2.getTrackbarPos('Threshold1', 'CAM')
    #Area2 = cv2.getTrackbarPos('Threshold2', 'CAM')

    #esse filtro cria um arco (linha imaginária) entre tons contrastantes na imagem, basicamente ele percebe a mudança drástica da intensidade de pixels criando uma
    #linha de contorno
    #peimiro parâmetro = imagem
    #segundo parâmetro = histerese (limite da saturação)
    #terçeiro parâmetro = histerese (limite da saturação)
    edge = cv2.Canny(cannyRoi,47,30)

    #matriz utilizada para realizar a dilatação da imagem
    kernel = np.ones((5,5),np.uint8)


    #filtro onde é feito o realce das bordas da imagem
    #primeiro parametro = imagem a ser filtrada
    #segundo parametro = matriz de filtro
    #terceiro parametro = número de vezes que o filtro será passado pela imagem
    dilate = cv2.dilate(edge,kernel,iterations=1)

    #chama função passando como primeiro parâmetro a região de interesse com os tratamentos aplicados
    #segundo parâmetro a imagem completa
    area2 = getContours(dilate,editedf)


    if area2 == None:
        cv2.rectangle(editedf,(380,160),(710,550), (0,255,0),3)
    else:
        cv2.rectangle(editedf,(380,160),(710,550), (0,0,255),3)
    view = cv2.resize(editedf,(640,480))
    cv2.imshow("CAM",view)
    
    if(area2 == None):
        startTime = time.time()
        if(endTime == 0):
            endTime = time.time()
            
        
    if(area2 != None):
        endTime = time.time()
        if(elapseTime(endTime,startTime) <= -5):
            saiu = 0
    
    if(elapseTime(startTime,endTime) <= -12 and elapseTime(startTime,endTime) >= -12.4 and saiu == 0):
        dataHora = time.strftime('%d-%m-%Y-%H-%M-%S')
        print('Salvando no banco')
        escreveDb()
        saiu = 1
        awaitTime = time.time()
        cv2.imwrite('/home/pi/Desktop/Imagens/foto '+dataHora+'.jpeg',editedf)
        
        
        
        
    if(cv2.waitKey(1) & 0xFF == ord('q')):
        break
    

vid.release()
cv2.destroyAllWindows()