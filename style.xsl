<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:output method="html" encoding="UTF-8" />

  <!-- Основной шаблон -->
  <xsl:template match="/">
    <html>
      <head>
        <title>Меню</title>
        <style>
          body {
            font-family: Arial, sans-serif;
            background-color:rgb(255, 255, 255); /* белый фон */
            margin: 0;
            padding: 20px;
            display: flex;
            flex-direction: column; /* Сюда добавлен вертикальный флекс */
            align-items: center; /* Центрирование по горизонтали */
          }

          .controls-container {
            display: flex;
            flex-direction: row; /* Горизонтальное расположение элементов */
            justify-content: flex-start; /* Выравнивание по левому краю */
            align-items: center; /* Вертикальное выравнивание */
            margin-bottom: 20px; /* Отступ снизу */
            width: 100%;
          }

          .controls-container input,
          .controls-container select,
          .controls-container button {
            margin: 5px;
            padding: 10px;
            font-size: 16px;
            cursor: pointer;
          }

          .controls-container input {
            width: 300px; /* Увеличиваем ширину поля поиска */
          }

          .controls-container select,
          .controls-container button {
            width: auto;
          }

          .main-title {
            width: 100%;
            text-align: center;
            font-size: 50px;
            font-weight: 900;
            color: rgb(243, 87, 20); /* Черный цвет для заголовка "Вкусно и Точка" */
            text-transform: uppercase;
            margin-bottom: 10px;
          }

          .sub-title {
            width: 100%;
            text-align: center;
            font-size: 40px;
            font-weight: 900; /* Добавляем жирность шрифта */
            color: black; /* Черный цвет для заголовка "Наше меню" */
            margin-bottom: 60px;
          }

          .dish-wrapper {
            display: flex;
            justify-content: space-between;
            align-items: center;
            width: 100%;
            max-width: 1200px; /* Увеличиваем ширину контейнера */
            margin-bottom: 40px; /* Увеличиваем расстояние между блюдами */
          }

          .dish {
            display: flex;
            flex-direction: column;
            margin-bottom: 20px;
            padding: 20px; /* Увеличиваем отступы внутри блока */
            background-color: #fff;
            border-radius: 12px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            width: 70%; /* Увеличиваем ширину каждого блюда */
            max-width: 700px; /* Увеличиваем максимальную ширину */
            position: relative;
          }

          .dish-content {
            flex-grow: 1;
            padding-right: 20px; /* Увеличиваем отступ справа */
          }

          .image-container {
            width: 300px; /* Увеличиваем размер изображения */
            height: 300px; /* Увеличиваем размер изображения */
            display: flex;
            align-items: center;
            justify-content: center;
            background-color: #f9f9f9;
            border-radius: 15px;
            box-shadow: 0 3px 6px rgba(0, 0, 0, 0.15);
            overflow: hidden;
            float: right;
            margin-left: 20px;
          }

          .image-container img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            border-radius: 15px;
          }

          .ingredients-container {
            background-color: #f0f0f0;
            padding: 15px; /* Увеличиваем отступ внутри ингредиентов */
            border-radius: 10px;
            width: 100%;
            margin-top: 15px; /* Увеличиваем отступ сверху */
          }

          .ingredient {
            font-size: 16px;
            color: #555;
            margin: 8px 0; /* Увеличиваем расстояние между ингредиентами */
            padding: 6px 10px;
            background-color: #e0e0e0;
            border-left: 4px solid #007b5e;
            display: block;
          }

          h1 {
            font-size: 22px;
            color: #333;
            text-transform: uppercase;
            margin-bottom: 8px;
          }

          .cooktime,
          .weight,
          .energy {
            font-style: italic;
            color: #777;
            font-size: 14px;
            margin-top: 5px;
          }

          ul {
            list-style-type: none;
            padding-left: 0;
            width: 100%;
          }

          li {
            margin-bottom: 5px;
          }

          .clear {
            clear: both;
          }
        </style>
      </head>
      <body>
        <div class="main-title">Вкусно - и Точка</div>
        <div class="sub-title">Наше меню</div>

        <xsl:for-each select="menu/dish">
          <div class="dish-wrapper">
            <div class="dish">
              <div class="dish-content">
                <h1><xsl:value-of select="title" /></h1>
                <p class="cooktime">Время приготовления: <xsl:value-of select="cooktime" /></p>
                <p class="weight">Вес: <xsl:value-of select="weight" /></p>
                <p class="energy">Энергетическая ценность: <xsl:value-of select="energy" /></p>
                <h2>Ингредиенты</h2>
                <div class="ingredients-container">
                  <ul>
                    <xsl:for-each select="composition/ingredient">
                      <li class="ingredient">
                        <xsl:value-of select="@amount" />
                        <xsl:text> </xsl:text>
                        <xsl:value-of select="@unit" /> - <xsl:value-of select="." />
                      </li>
                    </xsl:for-each>
                  </ul>
                </div>
              </div>
            </div>
            <div class="image-container">
              <img>
                <xsl:attribute name="src">
                  <xsl:value-of select="image"/>
                </xsl:attribute>
                <xsl:attribute name="alt">
                  <xsl:value-of select="title" />
                </xsl:attribute>
              </img>
            </div>
          </div>
          <div class="clear"></div>
        </xsl:for-each>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
