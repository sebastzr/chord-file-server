class Node(object):
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.uid = Uid(self.ip + ":" + repr(self.port))
        self.successor = self
        
        self.finger = []
        self.initfinger()

       
        self.log = logging.getLogger(repr(self.uid))
        self.log.setLevel(logging.DEBUG)
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(levelname)s - %(name)s - %(message)s')
        ch.setFormatter(formatter)
        self.log.addHandler(ch)

        #self.threadserverrpc = ThreadServerRPC(self)
        #self.threadserverrpc.start()
        # WIP
        #ThreadServerRPC(self).start()
        self.log.debug("node creation: uid={}".format(self.uid.value))
	
	def __repr__(self):
        return "<class Node - {hash}>".format(hash=self.uid)

    def initfinger(self):
        for i in range(0, self.uid.idlength):
            self.finger.append(None)

    def setsuccessor(self, successor):
        self.successor = successor
    
    def addToRing(self, newnode):
        '''
        @param newnode : nuevo Nodo para interactuar en el anillo
        '''
        self.log.debug("{} want to join {}".format(newnode.uid.value, self.uid.value))
        if newnode.uid.value != self.uid.value:
            
            self.updatesucc(newnode)
            self.updatefinger(newnode, self)
        else:

            self.log.error("Same uid than contacted node")
            raise Exception

    def updatesucc(self, newnode):
        if newnode.uid.value == self.uid.value: ## excepcion por ser el mismo valor
            raise Exception
        if self == self.successor:  ### si es el unico nodo y este es su mismo sucesor
            self.setsuccessor(newnode)
            newnode.setsuccessor(self)
        
        elif newnode.uid.isbetween(self.uid.value, self.successor.uid.value):  ### si el nuevo nodo esta entre el nodo y su susesor
            newnode.setsuccessor(self.successor)
            self.setsuccessor(newnode)
        else:
            self.successor.updatesucc(newnode) ## llama a la misma funcion del nodo preguntandole al sucesor

    def updatefinger(self, newnode, firstnode):
        '''
        Actualiza la Fingertable para todos el anillo en sentido de las manecillas del reloj
        finger es un diccionario {resp, key}
        resp` es el nodo responsable de`key`
        @param newnode: nodo nuevo a aplicar el update al anillo
        @param firstnode: nodo que se inicia a actualizar
        '''
        for i in range(0, self.uid.idlength):
            fingerkey = self.calcfinger(i)
            resp = self.lookup(fingerkey, useOnlySucc=True)
            self.finger[i] = {"resp": resp, "key": Key(fingerkey)}
            #self.finger[i] = self.lookupfinger(i, useOnlySucc=True)
        if firstnode is not self.successor:
            self.successor.updatefinger(newnode, firstnode)  ## recursivo a la actualizacion con es susesor

    def lookupfinger(self, k, useOnlySucc=False):
        '''
        Retorna el nodo responsable del finger k
        @param m: Id length del anillo (m = Key.idlength)
            el Ring esta constituido de  2^m nodos maximos
        '''
        return self.lookup(self.calcfinger(k), useOnlySucc)

            
    def lookup(self, key, useOnlySucc=False):
        
        if isinstance(key, Node):
            key = node.uid
        elif isinstance(key, Key):
            key = key
        elif isinstance(key, str):
            key = Key(key)
        else:
            raise Exception

        def getNextDichotomy(prevDichotomy, dichotomy, sign):
            fingmax = self.uid.idlength - 1
            fingmin = 0
            if prevDichotomy == dichotomy:
                raise ValueError("prevDichotomy & dichotomy are eq")
            if sign not in ["+", "-"]:
                raise Exception("getNetxtDichotomy used with invalid sign")
            elif sign is "+":
                if prevDichotomy < dichotomy:
                    return dichotomy + ((nfinger - dichotomy) / 2)
                else:
                    return dichotomy + ((prevDichotomy - dichotomy) / 2)
            elif sign is "-":
                if prevDichotomy < dichotomy:
                    return dichotomy - ((dichotomy - prevDichotomy) / 2)
                else:
                    return dichotomy - (dichotomy / 2)

        # lookup en el sucesor y pregunta al sucesor(falta optimizar)
        if useOnlySucc:
            # Self es sucesor
            if self.uid == key:
                return self
            # es self.successor el sucesor de la llave ? 
            if key.isbetween(self.uid.value, self.successor.uid.value):
                return self.successor
            
            return self.successor.lookup(key, useOnlySucc) ## llamad recursivo si optimizacion fingertable

        # usa la fingertable para optimizacion
        else:

            nfinger = self.uid.idlength
            fingmax = nfinger - 1

            
            # testea si key a lookup esta afuera de fingertable
            if key.isbetween(self.finger[fingmax]["resp"].uid + 1,
                             self.finger[0]["key"] - 1):
                # le pregunta al ultimo finger de la fingertable
                self.log.debug("lookup recurse to node {}".format(self.finger[fingmax]["resp"]))
                return self.finger[fingmax]["resp"].lookup(key, useOnlySucc)

            self.log.debug("key={}; finger(255)[resp]={}; finger(0)(key)={}\nfinger(255)(key)={}"
                           .format(key,
                                   Key(self.finger[fingmax]["resp"].uid + 1),
                                   Key(self.finger[0]["key"] - 1),
                                   self.finger[255]["key"])
                          )
            # self sabe la respuesta por que key < (self finger max)

            dichotomy = nfinger / 2
            prevDichotomy = 0
            # algoritmo por dicotomia
            while True:

                # finger(0) <= key < finger(dichotomy)
                # finger(dichotomy)[key] <= key <= finger(dichotomy)[resp]
                if key.isbetween(self.finger[dichotomy]["key"],
                                   self.finger[dichotomy]["resp"].uid.value):
                    self.log.debug("Assigns {} as succ for {}"
                            .format(self.finger[dichotomy]["resp"], key))
                    return self.finger[dichotomy]["resp"]
                    
                elif key.isbetween(self.finger[0]["key"] + 1,
                                 self.finger[dichotomy]["key"] - 1):
                    self.log.debug("key down to dichotomy: dichotomy:{} -"
                                   "prevDichotomy:{} -"
                                   "finger-dicho)(res)={} -"
                                   "finger-dicho)(key)={} -"
                                   "finger(0)[keyt]={}"
                                   .format(dichotomy,
                                           prevDichotomy,
                                           self.finger[dichotomy]["resp"],
                                           self.finger[dichotomy]["key"],
                                           self.finger[0]["key"]))

                    if self.finger[dichotomy - 1]["resp"] != self.finger[dichotomy]["resp"]:
                        if key.isbetween(self.finger[dichotomy - 1]["resp"].uid + 1,
                                       self.finger[dichotomy]["key"] - 1):
                            return self.finger[dichotomy - 1]["resp"].lookup(key, useOnlySucc)
                    try:
                        dichotomy_tmp = getNextDichotomy(prevDichotomy,
                                                         dichotomy,
                                                         "-")
                    except ValueError as e:
                        self.log.error(e)
                        raise
                    prevDichotomy = dichotomy
                    dichotomy = dichotomy_tmp

                # finger(dichotomy) < key <= finger(255)
                elif key.isbetween(self.finger[dichotomy]["resp"].uid + 1,
                                   self.finger[fingmax]["resp"].uid.value):
                    self.log.debug("UP to dichotomy: dichotomy:{} -"
                                   "prevDichotomy:{} -"
                                   "finger-dicho(resp)={} -"
                                   "finger(0)[key]={} - "
                                   "finger(dichotomy-1)[resp]={} -"
                                   "finger(dicho)[key]={}"
                                   .format(dichotomy,
                                           prevDichotomy,
                                           self.finger[dichotomy]["resp"],
                                           self.finger[0]["key"],
                                           self.finger[dichotomy - 1]["resp"].uid,
                                           self.finger[dichotomy]["key"],
                                           ))

                    # if finger dicho and next finger does not have same responsible
                    # it means there is a room for unreferenced node in self fingers
                    # if looked up key is in this room, we have to ask to the finger dichotomy
                    # to lookup for self, as self does not know the answer
                    if self.finger[dichotomy + 1]["resp"] != self.finger[dichotomy]["resp"]:
                        # test if key is in this room
                        # between the finger dichotomy responsible & the next finger key
                        if key.isbetween(self.finger[dichotomy]["resp"].uid + 1,
                                         self.finger[dichotomy + 1]["key"] - 1):
                            # let's ask to self.finger[dichotomy]
                            return self.finger[dichotomy]["resp"].lookup(key, useOnlySucc)
                    try:
                        dichotomy_tmp = getNextDichotomy(prevDichotomy,
                                                         dichotomy,
                                                         "+")
                    except ValueError as e:
                        self.log.error(e)
                        raise

                    prevDichotomy = dichotomy
                    dichotomy = dichotomy_tmp

                else:
                    self.log.error("OUT OF TOWN")
                    raise IndexError("lookup failed on properly catching the inclusion of the key.")

 
    def calcfinger(self, k):
        
        return self.uid + pow(2, k)

    def printFingers(self):
        for n, f in enumerate(self.finger):
            self.log.debug("TABLE: finger{0} : "
                "- key: {2} - resp: {1}"
                .format(n, f["resp"].uid, f["key"]))
            if f["resp"].uid.value != self.lookupfinger(n, useOnlySucc=True).uid.value:
                self.log.error("error between finger table and computed value")

    def printRing(self):
        succ = self.successor
        output = "Ring from {}]:\n".format(self.uid.value)
        key = self.successor.uid
        while key != self.uid:
            output += repr(key) + " -> "
            succ = succ.successor
            key = succ.uid
        self.log.debug(output)
