const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, AlignmentType, 
        HeadingLevel, WidthType, BorderStyle, VerticalAlign } = require('docx');
const fs = require('fs');

// Создание документа курсовой работы
const doc = new Document({
  styles: {
    default: {
      document: {
        run: { font: "Times New Roman", size: 28 } // 14pt
      }
    },
    paragraphStyles: [
      {
        id: "Title",
        name: "Title",
        basedOn: "Normal",
        run: { size: 32, bold: true, font: "Times New Roman" },
        paragraph: { spacing: { before: 0, after: 240 }, alignment: AlignmentType.CENTER }
      },
      {
        id: "Heading1",
        name: "Heading 1",
        basedOn: "Normal",
        next: "Normal",
        run: { size: 30, bold: true, font: "Times New Roman" },
        paragraph: { spacing: { before: 240, after: 180 }, outlineLevel: 0 }
      },
      {
        id: "Heading2",
        name: "Heading 2",
        basedOn: "Normal",
        next: "Normal",
        run: { size: 28, bold: true, font: "Times New Roman" },
        paragraph: { spacing: { before: 180, after: 120 }, outlineLevel: 1 }
      }
    ]
  },
  sections: [{
    properties: {
      page: {
        margin: { top: 1134, right: 1134, bottom: 1134, left: 1700 } // Левое поле шире для переплета
      }
    },
    children: [
      // Титульный лист
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 0, after: 120 },
        children: [new TextRun({
          text: "МИНОБРНАУКИ РОССИИ",
          size: 24,
          bold: true
        })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 120 },
        children: [new TextRun({
          text: "Федеральное государственное бюджетное",
          size: 24
        })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 120 },
        children: [new TextRun({
          text: "образовательное учреждение высшего образования",
          size: 24
        })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 120 },
        children: [new TextRun({
          text: "«Астраханский государственный университет имени В. Н. Татищева»",
          size: 24,
          bold: true
        })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 240, after: 120 },
        children: [new TextRun({ text: "Институт информационных технологий", size: 26 })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 480 },
        children: [new TextRun({ text: "Кафедра информационных технологий", size: 26 })]
      }),

      // Название работы
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 720, after: 240 },
        children: [new TextRun({
          text: "КУРСОВАЯ РАБОТА ПО ДИСЦИПЛИНЕ",
          size: 32,
          bold: true
        })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 240 },
        children: [new TextRun({
          text: "ТЕХНОЛОГИИ ПРОГРАММИРОВАНИЯ",
          size: 32,
          bold: true
        })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 240, after: 480 },
        children: [new TextRun({
          text: "Тема: Разработка REST-сервиса «Поликлиника»",
          size: 28,
          bold: true
        })]
      }),

      // Исполнитель
      new Paragraph({
        alignment: AlignmentType.RIGHT,
        spacing: { before: 480, after: 120 },
        children: [new TextRun({ text: "Выполнил:", size: 26 })]
      }),
      new Paragraph({
        alignment: AlignmentType.RIGHT,
        spacing: { after: 120 },
        children: [new TextRun({ text: "Студент группы: [Ваша группа]", size: 26 })]
      }),
      new Paragraph({
        alignment: AlignmentType.RIGHT,
        spacing: { after: 120 },
        children: [new TextRun({ text: "[Ваше ФИО]", size: 26 })]
      }),
      new Paragraph({
        alignment: AlignmentType.RIGHT,
        spacing: { before: 240, after: 120 },
        children: [new TextRun({ text: "Руководитель:", size: 26 })]
      }),
      new Paragraph({
        alignment: AlignmentType.RIGHT,
        spacing: { after: 960 },
        children: [new TextRun({ text: "Карпенко А. П.", size: 26 })]
      }),

      // Город и год
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 960 },
        children: [new TextRun({
          text: "Астрахань – 2025 г.",
          size: 28,
          bold: true
        })]
      }),

      // Начало основной части (новая страница)
      new Paragraph({ children: [new TextRun({ text: "", break: 5 })] }),

      // 1. Описание предметной области
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("1. Описание предметной области")]
      }),
      
      new Paragraph({
        spacing: { after: 120 },
        children: [new TextRun({
          text: "Предметная область: Поликлиника",
          bold: true
        })]
      }),
      new Paragraph({
        spacing: { after: 120 },
        children: [new TextRun("Объекты: Пациенты, Врачи, Связь пациентов и врачей (Приемы)")]
      }),
      new Paragraph({
        spacing: { after: 240 },
        children: [new TextRun("Примечание: Один врач может лечить многих пациентов. Один пациент может наблюдаться у многих врачей (по разным специализациям).")]
      }),

      // 1.1 Объект автоматизации
      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("1.1 Объект автоматизации")]
      }),
      new Paragraph({
        spacing: { after: 120 },
        children: [new TextRun("Современная поликлиника ежедневно обслуживает большое количество пациентов различными специалистами. Пациенты записываются на прием к врачам разных специализаций, проходят обследования и получают лечение.")]
      }),
      new Paragraph({
        spacing: { after: 120 },
        children: [new TextRun("Предлагается автоматизировать процесс учета пациентов, врачей и их взаимодействия. Система должна обеспечивать:")]
      }),
      new Paragraph({
        spacing: { after: 60 },
        children: [new TextRun("• Регистрацию новых пациентов и ведение их карточек")]
      }),
      new Paragraph({
        spacing: { after: 60 },
        children: [new TextRun("• Учет врачей с указанием специализации")]
      }),
      new Paragraph({
        spacing: { after: 60 },
        children: [new TextRun("• Фиксацию приемов пациентов у врачей")]
      }),
      new Paragraph({
        spacing: { after: 60 },
        children: [new TextRun("• Контроль за количеством приемов и нагрузкой врачей")]
      }),
      new Paragraph({
        spacing: { after: 240 },
        children: [new TextRun("• Предотвращение конфликтов при назначении приемов")]
      }),

      // 1.2 Формальное описание сущностей
      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("1.2 Формальное описание сущностей")]
      }),
      
      new Paragraph({
        spacing: { after: 120 },
        children: [new TextRun({ text: "Объект Пациент", bold: true })]
      }),
      new Paragraph({ children: [new TextRun("Характеристики:")] }),
      new Paragraph({ children: [new TextRun("• код пациента (уникальный идентификатор)")] }),
      new Paragraph({ children: [new TextRun("• ФИО пациента")] }),
      new Paragraph({ children: [new TextRun("• дата рождения")] }),
      new Paragraph({ children: [new TextRun("• номер телефона")] }),
      new Paragraph({ children: [new TextRun("• адрес проживания")] }),
      new Paragraph({ spacing: { after: 180 }, children: [new TextRun("• номер полиса ОМС")] }),

      new Paragraph({
        spacing: { after: 120 },
        children: [new TextRun({ text: "Объект Врач", bold: true })]
      }),
      new Paragraph({ children: [new TextRun("Характеристики:")] }),
      new Paragraph({ children: [new TextRun("• код врача (уникальный идентификатор)")] }),
      new Paragraph({ children: [new TextRun("• ФИО врача")] }),
      new Paragraph({ children: [new TextRun("• специализация (терапевт, хирург, кардиолог и т.д.)")] }),
      new Paragraph({ children: [new TextRun("• номер кабинета")] }),
      new Paragraph({ children: [new TextRun("• номер телефона")] }),
      new Paragraph({ spacing: { after: 180 }, children: [new TextRun("• стаж работы в годах")] }),

      new Paragraph({
        spacing: { after: 120 },
        children: [new TextRun({ text: "Объект Прием (Связь пациента и врача)", bold: true })]
      }),
      new Paragraph({ children: [new TextRun("Характеристики:")] }),
      new Paragraph({ children: [new TextRun("• код записи (уникальный идентификатор)")] }),
      new Paragraph({ children: [new TextRun("• ссылка на пациента")] }),
      new Paragraph({ children: [new TextRun("• ссылка на врача")] }),
      new Paragraph({ children: [new TextRun("• дата приема")] }),
      new Paragraph({ children: [new TextRun("• время приема")] }),
      new Paragraph({ children: [new TextRun("• диагноз (может быть пустым)")] }),
      new Paragraph({ spacing: { after: 240 }, children: [new TextRun("• статус приема (запланирован, завершен, отменен)")] }),

      // 1.3 Описание сущностей в табличном виде
      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("1.3 Описание сущностей в табличном виде")]
      }),

      // Таблица Пациент
      new Paragraph({
        spacing: { before: 120, after: 120 },
        children: [new TextRun({ text: "Таблица «Пациент»", bold: true })]
      }),
      new Table({
        width: { size: 100, type: WidthType.PERCENTAGE },
        rows: [
          new TableRow({
            children: [
              new TableCell({
                width: { size: 30, type: WidthType.PERCENTAGE },
                shading: { fill: "CCCCCC" },
                children: [new Paragraph({
                  alignment: AlignmentType.CENTER,
                  children: [new TextRun({ text: "Название поля", bold: true })]
                })]
              }),
              new TableCell({
                width: { size: 20, type: WidthType.PERCENTAGE },
                shading: { fill: "CCCCCC" },
                children: [new Paragraph({
                  alignment: AlignmentType.CENTER,
                  children: [new TextRun({ text: "Тип данных", bold: true })]
                })]
              }),
              new TableCell({
                width: { size: 50, type: WidthType.PERCENTAGE },
                shading: { fill: "CCCCCC" },
                children: [new Paragraph({
                  alignment: AlignmentType.CENTER,
                  children: [new TextRun({ text: "Описание", bold: true })]
                })]
              })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ children: [new Paragraph("ID (PK)")] }),
              new TableCell({ children: [new Paragraph("INTEGER")] }),
              new TableCell({ children: [new Paragraph("Уникальный идентификатор пациента. Первичный ключ.")] })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ children: [new Paragraph("FIO")] }),
              new TableCell({ children: [new Paragraph("TEXT")] }),
              new TableCell({ children: [new Paragraph("ФИО пациента")] })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ children: [new Paragraph("BIRTH_DATE")] }),
              new TableCell({ children: [new Paragraph("DATE")] }),
              new TableCell({ children: [new Paragraph("Дата рождения пациента")] })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ children: [new Paragraph("PHONE")] }),
              new TableCell({ children: [new Paragraph("TEXT")] }),
              new TableCell({ children: [new Paragraph("Номер телефона пациента")] })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ children: [new Paragraph("ADDRESS")] }),
              new TableCell({ children: [new Paragraph("TEXT")] }),
              new TableCell({ children: [new Paragraph("Адрес проживания пациента")] })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ children: [new Paragraph("INSURANCE_NUMBER")] }),
              new TableCell({ children: [new Paragraph("TEXT")] }),
              new TableCell({ children: [new Paragraph("Номер полиса ОМС")] })
            ]
          })
        ]
      }),

      // Заключение
      new Paragraph({ children: [new TextRun({ text: "", break: 2 })] }),
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("Заключение")]
      }),
      new Paragraph({
        spacing: { after: 120 },
        children: [new TextRun("Разработанный REST-сервис «Поликлиника» реализует все требования курсового проекта:")]
      }),
      new Paragraph({ children: [new TextRun("✓ Полноценная база данных PostgreSQL с 3 связанными таблицами")] }),
      new Paragraph({ children: [new TextRun("✓ CRUD операции для всех сущностей")] }),
      new Paragraph({ children: [new TextRun("✓ Валидация данных и обработка исключений")] }),
      new Paragraph({ children: [new TextRun("✓ Форматирование ошибок в виде Problem Details")] }),
      new Paragraph({ children: [new TextRun("✓ Логирование всех операций")] }),
      new Paragraph({ children: [new TextRun("✓ Unit-тестирование с демонстрацией работы")] }),
      new Paragraph({
        spacing: { before: 240 },
        children: [new TextRun("✓ Автоматическая документация API")]
      }),
      new Paragraph({
        spacing: { before: 240 },
        children: [new TextRun("Сервис готов к использованию и может быть расширен дополнительными функциями по мере необходимости.")]
      })
    ]
  }]
});

// Сохранение документа
Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("/mnt/user-data/outputs/Курсовая_работа_Поликлиника.docx", buffer);
  console.log("✅ Документ курсовой работы создан успешно!");
  console.log("📄 Файл: Курсовая_работа_Поликлиника.docx");
});
