class Data:
  def __init__(self, hist):
    self.hist = hist
    self.update_indicators()
    
  def update_indicators(self):
    macd, macdsignal, macdhist = talib.MACD(self.hist.Close)
    real = talib.RSI(self.hist.Close, timeperiod=14)
    mom = talib.MOM(self.hist.Close)
    sma_mom14 = talib.SMA(mom, timeperiod=14)
    upperband, middleband, lowerband = talib.BBANDS(self.hist.Close, timeperiod=20)
    ema12 = talib.EMA(self.hist.Close, timeperiod=12)
    ema26 = talib.EMA(self.hist.Close, timeperiod=26)
    ema50 = talib.EMA(self.hist.Close, timeperiod=50)
    ema200 = talib.EMA(self.hist.Close, timeperiod=200)
    adx = talib.ADX(self.hist.High, self.hist.Low, self.hist.Close, timeperiod=14)
    minus_di = talib.MINUS_DI(self.hist.High, self.hist.Low, self.hist.Close, timeperiod=14)
    plus_di = talib.PLUS_DI(self.hist.High, self.hist.Low, self.hist.Close, timeperiod=14)
    aroondown, aroonup = talib.AROON(self.hist.High, self.hist.Low, timeperiod=14)
  
    self.hist['MACD'] = macd
    self.hist['Signal Line'] = macdsignal
    self.hist['RSI'] = real
    self.hist['MOM'] = mom
    self.hist['SMA_MOM_14'] = sma_mom14
    self.hist['BB_upper'] = upperband
    self.hist['BB_middle'] = middleband
    self.hist['BB_lower'] = lowerband
    self.hist['EMA12'] = ema12
    self.hist['EMA26'] = ema26
    self.hist['EMA50'] = ema50
    self.hist['EMA200'] = ema200
    self.hist['ADX'] = adx
    self.hist['Minus DI'] = minus_di
    self.hist['Plus DI'] = plus_di
    self.hist['AROON up'] = aroonup
    self.hist['AROON down'] = aroondown

    self.hist['MACD_Test'] = self.hist.apply(lambda row: self.MACD_signal(row), axis=1)
    self.hist['RSI_Test'] = self.hist.apply(lambda row: self.RSI_signal(row), axis=1)
    self.hist['MOM_Test'] = self.hist.apply(lambda row: self.MOM_signal(row), axis=1)
    self.hist['BB_Test'] = self.hist.apply(lambda row: self.BB_signal(row), axis=1)
    self.hist['EMA_Short_Test'] = self.hist.apply(lambda row: self.EMA_short_term_signal(row), axis=1)
    self.hist['EMA_Long_Test'] = self.hist.apply(lambda row: self.EMA_long_term_signal(row), axis=1)
    self.hist['ADX_Test'] = self.hist.apply(lambda row: self.ADX_signal(row), axis=1)

    self.hist["Prediction Labels"] = self.create_labels( self.hist, "Close", window_size=14)
  # MACD Indicator detects changes in momentum and can help identify buy sell locations
  def MACD_signal(self, signal):
    flag = 0
    for i in range(0, len(signal)):
      if signal['MACD'] > signal['Signal Line']:
          flag = 1
      elif signal['MACD'] < signal['Signal Line']:
          flag = -1
      else:
        flag = 0
    return flag

  # Relative Strength Index used to identify momentum, market conditions, and
  # provide warning for unusual price movements
  def RSI_signal(self, signal):
    flag = 0
    for i in range(0, len(signal)):
      if signal['RSI'] > 70:
          flag = -1
      elif signal['RSI'] < 30:
          flag = 1
      else:
        flag = 0
    return flag

  # The momentum indicator is used to determine the strength of a price movement.
  # Using crossover strategy with SMA 14
  def MOM_signal(self, signal):
    flag = 0
    for i in range(0, len(signal)):
      if signal['MOM'] > signal['SMA_MOM_14']:
          flag = 1
      elif signal['MOM'] < signal['SMA_MOM_14']:
          flag = -1
      else:
        flag = 0
    return flag

    # Bollinger bands provides insight into how an asset typically trades. Here the
    # sell point occurs when close prices breaks lower band and buy occurs when
    # close breaks upper band

  def BB_signal(self, signal):
    flag = 0
    for i in range(0, len(signal)):
      if signal['Close'] >= signal['BB_upper']:
          flag = 1
      elif signal['Close'] <= signal['BB_lower']:
          flag = -1
      else:
        flag = 0
    return flag

    # Exponential Moving Average uses ema12 and ema26 to determine the short term
    # outlook and decide when to trade. Also places more weight on newer prices

  def EMA_short_term_signal(self, signal):
    flag = 0
    for i in range(0, len(signal)):
      if signal['EMA12'] > signal['EMA26']:
          flag = 1
      elif signal['EMA12'] < signal['EMA26']:
          flag = -1
      else:
        flag = 0
    return flag

    # Exponential Moving Average uses ema50 and ema200 to determine the long term
    # outlook and decide when to trade. Also places more weight on newer prices

  def EMA_long_term_signal(self, signal):
    flag = 0
    for i in range(0, len(signal)):
      if signal['EMA50'] > signal['EMA200']:
          flag = 1
      elif signal['EMA50'] < signal['EMA200']:
          flag = -1
      else:
        flag = 0
    return flag
  
  def ADX_signal(self, signal):
    flag = 0
    for i in range(0, len(signal)):
      if signal['ADX'] > 25 and signal['Plus DI'] > signal['Minus DI']:
          flag = 1
      elif signal['ADX'] < 20 and signal['Plus DI'] < signal['Minus DI']:
          flag = -1
      else:
        flag = 0
    return flag
    
  def AROON_signal(self, signal):
    flag = 0
    for i in range(0, len(signal)):
      if signal['AROON up'] > signal['AROON down']:
          flag = 1
      elif signal['AROON up'] < signal['AROON down']:
          flag = -1
      else:
        flag = 0
    return flag
    
  def get(self):
    return self.hist
  
  def create_labels(self, df, col_name="Close", window_size=11):
        """
        Data is labeled as per the logic in research paper
        Label code : BUY => 1, SELL => 0, HOLD => 2
        params :
            df => Dataframe with data
            col_name => name of column which should be used to determine strategy
        returns : numpy array with integer codes for labels with
                  size = total-(window_size)+1
        """

        row_counter = 0
        total_rows = len(df)
        labels = np.zeros(total_rows)
        labels[:] = np.nan
        print("Calculating labels")

        while row_counter < total_rows:
            if row_counter >= window_size - 1:
                window_begin = row_counter - (window_size - 1)
                window_end = row_counter
                window_middle = (window_begin + window_end) // 2

                min_ = np.inf
                min_index = -1
                max_ = -np.inf
                max_index = -1
                for i in range(window_begin, window_end + 1):
                    price = df.iloc[i][col_name]
                    if price < min_:
                        min_ = price
                        min_index = i
                    if price > max_:
                        max_ = price
                        max_index = i
                if max_index == window_middle:
                    labels[window_middle] = -1
                elif min_index == window_middle:
                    labels[window_middle] = 1
                else:
                    labels[window_middle] = 0

            row_counter = row_counter + 1
        return labels


class NeuralNetwork:
    def __init__(self, _input, hidden, output, model=None):
        if model == None:
            self.input_nodes = _input
            self.hidden_nodes = hidden
            self.output_nodes = output
            self.model = self.createModel()
        else:
            self.input_nodes = _input
            self.hidden_nodes = hidden
            self.output_nodes = output
            self.model = model

    def createModel(self, child_weights=None):

        model = tf.keras.Sequential()

        _input_shape = tf.keras.Input(shape=(self.input_nodes,))

        _input = tf.keras.layers.Dense(
            units=self.input_nodes, activation='relu')
        
        hidden = tf.keras.layers.Dense(
            units=self.hidden_nodes, activation='relu')
        
        hidden2 = tf.keras.layers.Dense(
            units=self.hidden_nodes, activation='relu')
        
        output = tf.keras.layers.Dense(
            units=self.output_nodes, activation="sigmoid")
        
        model.add(_input_shape)
        model.add(_input)
        model.add(hidden)
        model.add(hidden2)
        model.add(output)
        if child_weights:
            model.set_weights(child_weights)
        model.summary()
        return model

    def copy(self):
        modelCopy = self.createModel()
        weights = self.model.get_weights()
        weight_copies = weights.copy()
        # for i in range(len(weights)):
        #     weight_copies.append(weights[i].clone())
        modelCopy.set_weights(weight_copies)
        return NeuralNetwork(self.input_nodes, self.hidden_nodes, self.output_nodes, model=modelCopy)

    def predict(self, inputs):
        ys = self.model.predict(inputs)
        return ys
        
    def train(self, X_train, y_train):
      adam = tf.keras.optimizers.Adam(learning_rate=0.001)
      self.model.compile(
                      optimizer=adam,
                      loss='mse'
                      )
      self.model.fit(X_train, y_train, epochs = 100)

