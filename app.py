app.py
// NOTA: Este componente requiere las siguientes librerías cargadas vía CDN:
// 1. jsPDF para generar PDFs: <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
// 2. docx para generar Word: <script src="https://cdn.jsdelivr.net/npm/docx@8.5.0/build/index.min.js"></script>

import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Info, AlertTriangle, CheckCircle, Calendar, Pill } from 'lucide-react';

const ToxicityManagementSystem = () => {
  const [mode, setMode] = useState(null);
  const [selectedOrgan, setSelectedOrgan] = useState('');
  const [selectedToxicity, setSelectedToxicity] = useState('');
  const [selectedGrade, setSelectedGrade] = useState('');
  const [showCorticoidRecommendation, setShowCorticoidRecommendation] = useState(false);
  const [showAdditionalInfo, setShowAdditionalInfo] = useState(false);
  
  // Calculadora estados
  const [currentDose, setCurrentDose] = useState({ breakfast: '', lunch: '', dinner: '', total: '' });
  const [weeksToTaper, setWeeksToTaper] = useState('');
  const [weeklyReduction, setWeeklyReduction] = useState('');
  const [taperSchedule, setTaperSchedule] = useState(null);
  const [selectedCorticoid, setSelectedCorticoid] = useState('prednisona');
  const [patientWeight, setPatientWeight] = useState('');
  const [librariesLoaded, setLibrariesLoaded] = useState(false);

  // Cargar librerías para generación de documentos
  useEffect(() => {
    const loadLibraries = () => {
      // Marcar como cargado después de 2 segundos o cuando las librerías estén disponibles
      const checkInterval = setInterval(() => {
        if (window.jspdf && window.docx) {
          setLibrariesLoaded(true);
          clearInterval(checkInterval);
        }
      }, 500);
      
      // Timeout de seguridad - marcar como cargado después de 3 segundos
      setTimeout(() => {
        setLibrariesLoaded(true);
        clearInterval(checkInterval);
      }, 3000);
      
      // Cargar jsPDF si no está disponible
      if (!window.jspdf) {
        const jspdfScript = document.createElement('script');
        jspdfScript.src = 'https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js';
        jspdfScript.async = true;
        jspdfScript.onerror = () => console.error('Error cargando jsPDF');
        document.head.appendChild(jspdfScript);
      }
      
      // Cargar docx si no está disponible
      if (!window.docx) {
        const docxScript = document.createElement('script');
        docxScript.src = 'https://cdn.jsdelivr.net/npm/docx@8.5.0/build/index.min.js';
        docxScript.async = true;
        docxScript.onerror = () => console.error('Error cargando docx');
        document.head.appendChild(docxScript);
      }
    };
    
    loadLibraries();
  }, []);

  // Equivalencias de corticoides (en relación a prednisona)
  const corticoidEquivalence = {
    prednisona: { 
      factor: 1, 
      presentations: [2.5, 5, 10, 30], 
      name: 'Prednisona', 
      commercial: 'Dacortin®',
      availableDoses: 'Comprimidos: 2.5 mg, 5 mg, 10 mg, 30 mg'
    },
    metilprednisolona: { 
      factor: 0.8, 
      presentations: [4, 16, 40], 
      name: 'Metilprednisolona', 
      commercial: 'Urbason®',
      availableDoses: 'Comprimidos: 4 mg, 16 mg, 40 mg'
    },
    dexametasona: { 
      factor: 0.15, 
      presentations: [0.5, 0.75, 1, 4], 
      name: 'Dexametasona', 
      commercial: 'Fortecortin®',
      availableDoses: 'Comprimidos: 0.5 mg, 0.75 mg, 1 mg, 4 mg'
    }
  };

  const organSystems = {
    'Cutáneo': [
      'Dermatitis maculopapular',
      'Prurito',
      'Vitiligo',
      'Psoriasis',
      'Liquen plano',
      'Penfigoide ampolloso',
      'Síndrome de Stevens-Johnson'
    ],
    'Endocrino': [
      'Hipotiroidismo primario',
      'Hipertiroidismo/Tiroiditis',
      'Hipofisitis',
      'Diabetes mellitus tipo 1',
      'Insuficiencia suprarrenal primaria',
      'Insuficiencia suprarrenal secundaria'
    ],
    'Hepático': [
      'Hepatitis',
      'Colangitis',
      'Elevación de transaminasas'
    ],
    'Pancreático': [
      'Pancreatitis',
      'Elevación de lipasa asintomática',
      'Elevación de amilasa'
    ],
    'Gastrointestinal': [
      'Diarrea/Colitis/Enterocolitis',
      'Gastritis',
      'Colitis microscópica',
      'Perforación intestinal'
    ],
    'Pulmonar': [
      'Neumonitis',
      'Enfermedad intersticial pulmonar',
      'Neumonitis organizada',
      'Sarcoidosis pulmonar'
    ],
    'Reumatológico': [
      'Artritis inflamatoria',
      'Artralgia',
      'Mialgia',
      'Miositis',
      'Polimialgia reumática',
      'Síndrome sicca/Sjögren',
      'Vasculitis'
    ],
    'Neurológico': [
      'Meningitis aséptica',
      'Encefalitis',
      'Síndrome de Guillain-Barré',
      'Miastenia gravis',
      'Neuropatía periférica',
      'Mielitis transversa',
      'Síndrome miasténico-miosítico-miocardítico'
    ],
    'Cardiovascular': [
      'Miocarditis',
      'Pericarditis',
      'Miocarditis + Miositis',
      'Arritmias',
      'Bloqueo cardíaco',
      'Vasculitis coronaria'
    ],
    'Renal': [
      'Nefritis intersticial aguda',
      'Glomerulonefritis',
      'Elevación de creatinina',
      'Síndrome nefrótico'
    ],
    'Ocular': [
      'Uveítis',
      'Ojo seco',
      'Conjuntivitis',
      'Miopatía orbitaria',
      'Neuritis óptica'
    ],
    'Hematológico': [
      'Anemia hemolítica autoinmune',
      'Trombocitopenia',
      'Neutropenia',
      'Pancitopenia',
      'Linfohistiocitosis hemofagocítica'
    ]
  };

  const toxicityGrades = {
    'G1': {
      description: 'Asintomático o síntomas leves; solo observación clínica; intervención no indicada',
      action: 'Continuar inmunoterapia con monitorización estrecha'
    },
    'G2': {
      description: 'Síntomas moderados; intervención médica indicada; limita actividades instrumentales de la vida diaria',
      action: 'Considerar interrumpir temporalmente la inmunoterapia'
    },
    'G3': {
      description: 'Síntomas severos; hospitalización posible; limita el autocuidado de la vida diaria',
      action: 'Interrumpir inmunoterapia; considerar hospitalización'
    },
    'G4': {
      description: 'Consecuencias potencialmente mortales; intervención urgente indicada',
      action: 'Suspender permanentemente inmunoterapia; hospitalización urgente'
    }
  };

  const getDetailedRecommendation = () => {
    if (!selectedOrgan || !selectedToxicity || !selectedGrade) return null;

    const recommendations = {
      'Gastrointestinal': {
        'Diarrea/Colitis/Enterocolitis': {
          'G1': {
            corticoid: 'No indicado inicialmente',
            management: 'Dieta baja en fibra, loperamida. Continuar ICI con monitorización',
            monitoring: 'Control semanal de síntomas',
            ici: 'Continuar'
          },
          'G2': {
            corticoid: 'Prednisona (Dacortin®) 40-60 mg/día VO',
            management: 'Si no mejora en 3-5 días: considerar infliximab o vedolizumab. Colonoscopia si persistente',
            monitoring: 'Calprotectina fecal. Colonoscopia para evaluar respuesta',
            ici: 'Interrumpir temporalmente',
            taper: '4-6 semanas'
          },
          'G3': {
            corticoid: 'Metilprednisolona (Urbason®) 1-2 mg/kg/día IV',
            management: 'Hospitalización. Infliximab 5 mg/kg si corticorrefractario. Vedolizumab alternativa',
            monitoring: 'Colonoscopia urgente. Calprotectina fecal. Cultivo C. difficile, CMV en biopsia',
            ici: 'Suspender',
            taper: '6-8 semanas'
          },
          'G4': {
            corticoid: 'Metilprednisolona (Urbason®) 2 mg/kg/día IV',
            management: 'UCI si necesario. Infliximab precoz. Descartar megacolon tóxico/perforación',
            monitoring: 'TC abdominal. Valorar cirugía',
            ici: 'Suspender permanentemente',
            taper: '≥8 semanas'
          }
        }
      },
      'Pulmonar': {
        'Neumonitis': {
          'G1': {
            corticoid: 'No indicado si asintomático',
            management: 'TC torácico de control. Descartar infección/progresión tumoral',
            monitoring: 'TC cada 2-4 semanas',
            ici: 'Puede continuar con monitorización estrecha'
          },
          'G2': {
            corticoid: 'Prednisona (Dacortin®) 1 mg/kg/día (max 60-80 mg)',
            management: 'TC torácico. Descartar infección (lavado broncoalveolar si necesario)',
            monitoring: 'Función pulmonar. TC a las 48-72h',
            ici: 'Interrumpir',
            taper: '4-6 semanas'
          },
          'G3': {
            corticoid: 'Metilprednisolona (Urbason®) 1-2 mg/kg/día IV',
            management: 'Hospitalización. Si no mejora en 72h: Tocilizumab 8 mg/kg o Infliximab 5 mg/kg',
            monitoring: 'Oxigenoterapia. TC urgente. Saturación O2 continua',
            ici: 'Suspender',
            taper: '≥6-8 semanas'
          },
          'G4': {
            corticoid: 'Metilprednisolona (Urbason®) 1000 mg/día IV x 3 días',
            management: 'UCI. Tocilizumab o Infliximab precoz. ECMO si necesario',
            monitoring: 'Ventilación mecánica si precisa',
            ici: 'Suspender permanentemente',
            taper: 'Individualizado, muy prolongado'
          }
        }
      },
      'Hepático': {
        'Hepatitis': {
          'G1': {
            corticoid: 'No indicado',
            labValues: 'AST/ALT: 1-3× LSN',
            management: 'Monitorización semanal de transaminasas. Descartar otras causas',
            monitoring: 'AST, ALT, bilirrubina cada 1-2 semanas',
            ici: 'Continuar con precaución'
          },
          'G2': {
            corticoid: 'Prednisona (Dacortin®) 0.5-1 mg/kg/día si persistente',
            labValues: 'AST/ALT: 3-5× LSN',
            management: 'Suspender hepatotóxicos. Considerar biopsia hepática',
            monitoring: 'Transaminasas 2x/semana',
            ici: 'Interrumpir temporalmente',
            taper: '4-6 semanas'
          },
          'G3': {
            corticoid: 'Prednisona (Dacortin®) 1-2 mg/kg/día',
            labValues: 'AST/ALT: 5-20× LSN, o Bilirrubina: 3-10× LSN',
            management: 'Hospitalización. Si no respuesta en 48-72h: MMF 1g/12h o Tocilizumab',
            monitoring: 'Biopsia hepática. TP, Factor V, bilirrubina diaria',
            ici: 'Suspender',
            taper: '6-8 semanas'
          },
          'G4': {
            corticoid: 'Metilprednisolona (Urbason®) 2 mg/kg/día IV',
            labValues: 'AST/ALT: >20× LSN, o Bilirrubina: >10× LSN',
            management: 'UCI. Considerar trasplante hepático si fallo hepático fulminante',
            monitoring: 'Función hepática cada 6-12h',
            ici: 'Suspender permanentemente',
            taper: 'Prolongado'
          }
        }
      },
      'Pancreático': {
        'Pancreatitis': {
          'G1': {
            corticoid: 'No indicado',
            labValues: 'Lipasa/Amilasa: 1-2× LSN, asintomático',
            management: 'Dieta normal. Monitorización. Descartar otras causas',
            monitoring: 'Lipasa, amilasa cada semana',
            ici: 'Continuar con precaución'
          },
          'G2': {
            corticoid: 'Prednisona (Dacortin®) 0.5-1 mg/kg/día si persistente',
            labValues: 'Lipasa/Amilasa: >2-5× LSN, dolor abdominal moderado',
            management: 'Dieta absoluta 24-48h. Analgesia. TC abdominal',
            monitoring: 'Lipasa, amilasa diarias. TC si empeora',
            ici: 'Interrumpir temporalmente',
            taper: '4-6 semanas'
          },
          'G3': {
            corticoid: 'Metilprednisolona (Urbason®) 1-2 mg/kg/día IV',
            labValues: 'Lipasa/Amilasa: >5× LSN, dolor intenso, íleo',
            management: 'Hospitalización. NPO. Fluidos IV. TC abdominal. Si no mejora: considerar CPRE',
            monitoring: 'Lipasa, amilasa, calcio, LDH diarias. Escala de Ranson/APACHE II',
            ici: 'Suspender',
            taper: '6-8 semanas'
          },
          'G4': {
            corticoid: 'Metilprednisolona (Urbason®) 2 mg/kg/día IV',
            labValues: 'Pancreatitis necrotizante, shock, fallo multiorgánico',
            management: 'UCI. Soporte hemodinámico. Nutrición parenteral. Considerar necrosectomía',
            monitoring: 'TC con contraste. Monitorización intensiva',
            ici: 'Suspender permanentemente',
            taper: 'Muy prolongado'
          }
        },
        'Elevación de lipasa asintomática': {
          'G1': {
            corticoid: 'No indicado',
            labValues: 'Lipasa: 1-2× LSN, sin síntomas',
            management: 'Monitorización semanal. No requiere tratamiento',
            monitoring: 'Lipasa semanal',
            ici: 'Continuar'
          },
          'G2': {
            corticoid: 'No indicado habitualmente',
            labValues: 'Lipasa: 2-5× LSN, sin dolor ni síntomas',
            management: 'Monitorización estrecha. Considerar TC si aumenta',
            monitoring: 'Lipasa 2x/semana',
            ici: 'Puede continuar con monitorización',
            taper: 'No aplicable'
          }
        }
      },
      'Endocrino': {
        'Hipofisitis': {
          'G2': {
            corticoid: 'Hidrocortisona 15-20 mg/día (10 mg mañana + 5 mg tarde) - reemplazo',
            management: 'RM hipofisaria. Valorar resto de ejes. Reemplazo de T4 si precisa',
            monitoring: 'Cortisol 8h, ACTH, TSH, FT4, LH, FSH, testosterona/estradiol',
            ici: 'Puede continuar con reemplazo hormonal',
            taper: 'No aplicable - reemplazo permanente'
          },
          'G3': {
            corticoid: 'Hidrocortisona 50-100 mg IV/6h (dosis de estrés) si crisis suprarrenal',
            management: 'Hospitalización. Tratamiento agudo de crisis suprarrenal',
            monitoring: 'Electrolitos, glucemia, TA',
            ici: 'Interrumpir hasta estabilización',
            taper: 'Descenso a dosis de reemplazo'
          }
        },
        'Insuficiencia suprarrenal primaria': {
          'G2': {
            corticoid: 'Hidrocortisona 15-20 mg/día + Fludrocortisona 0.1 mg/día',
            management: 'Test de ACTH. Educación sobre dosis de estrés',
            monitoring: 'Cortisol 8h, ACTH, Na, K, TA',
            ici: 'Puede continuar con reemplazo',
            taper: 'Reemplazo permanente'
          },
          'G3': {
            corticoid: 'Hidrocortisona 50-100 mg IV/6-8h',
            management: 'Crisis suprarrenal: sueroterapia, corrección electrolitos',
            monitoring: 'UCI/Hospitalización. Glucemia, electrolitos horarios',
            ici: 'Interrumpir hasta estabilización',
            taper: 'Descenso a dosis de reemplazo'
          }
        },
        'Diabetes mellitus tipo 1': {
          'G2': {
            corticoid: 'NO INDICADO - contraindicado',
            management: 'Insulinoterapia inmediata. Pauta basal-bolo',
            monitoring: 'Glucemias capilares, HbA1c, péptido C, Ac anti-GAD',
            ici: 'Puede continuar con control glucémico estricto',
            taper: 'No aplicable'
          },
          'G3': {
            corticoid: 'NO INDICADO',
            management: 'Cetoacidosis: hospitalización, insulina IV, sueroterapia, K+',
            monitoring: 'Glucemia horaria, pH, anion gap, cetonuria',
            ici: 'Interrumpir hasta resolución de cetoacidosis',
            taper: 'No aplicable'
          }
        }
      },
      'Cardiovascular': {
        'Miocarditis': {
          'G2': {
            corticoid: 'Metilprednisolona (Urbason®) 500-1000 mg IV/día x 3 días',
            management: 'Hospitalización nivel 2-3. ECG monitorización. Ecocardiograma. RMN cardíaca',
            monitoring: 'Troponina I, NT-proBNP, ECG diario',
            ici: 'Suspender',
            taper: 'Tras 3 días IV → Prednisona 1 mg/kg, descenso 10 mg/semana'
          },
          'G3': {
            corticoid: 'Metilprednisolona (Urbason®) 1000 mg IV/día x 3-5 días',
            management: 'UCI. Si troponina no baja >50% o inestabilidad: Tocilizumab, MMF o ATG',
            monitoring: 'Monitorización cardíaca continua. Troponina diaria. RMN',
            ici: 'Suspender permanentemente',
            taper: 'Muy prolongado (meses). Descenso 10 mg/semana desde 80 mg'
          },
          'G4': {
            corticoid: 'Metilprednisolona (Urbason®) 1000 mg IV/día + 2ª línea inmediata',
            management: 'UCI. ECMO/LVAD si shock cardiogénico. Tocilizumab + ATG precoz',
            monitoring: 'Monitorización invasiva. Marcadores cada 6h',
            ici: 'Suspender permanentemente',
            taper: 'Individualizado, muy prolongado'
          }
        }
      },
      'Neurológico': {
        'Miastenia gravis': {
          'G2': {
            corticoid: 'Prednisona (Dacortin®) 0.5-1 mg/kg/día',
            management: 'Piridostigmina 60 mg/8h (titular). Ac anti-receptor ACh. EMG',
            monitoring: 'Función respiratoria. Test edrofonio',
            ici: 'Interrumpir',
            taper: '6-8 semanas'
          },
          'G3': {
            corticoid: 'Metilprednisolona (Urbason®) 1-2 mg/kg/día + IGIV o plasmaféresis',
            management: 'Hospitalización. IGIV 2 g/kg en 2-5 días. Piridostigmina',
            monitoring: 'Capacidad vital forzada. Intubación si crisis',
            ici: 'Suspender',
            taper: 'Prolongado'
          }
        },
        'Síndrome de Guillain-Barré': {
          'G2': {
            corticoid: 'Metilprednisolona (Urbason®) 2-4 mg/kg/día (trial)',
            management: 'Neurología. Punción lumbar. IGIV si progresión',
            monitoring: 'Fuerza muscular. Función respiratoria',
            ici: 'Interrumpir',
            taper: 'Lento'
          },
          'G3': {
            corticoid: 'Metilprednisolona (Urbason®) 1g/día x 5 días + IGIV o plasmaféresis',
            management: 'UCI. IGIV 0.4 g/kg/día x 5 días o plasmaféresis',
            monitoring: 'Ventilación mecánica si precisa',
            ici: 'Suspender',
            taper: 'Muy prolongado'
          }
        }
      },
      'Reumatológico': {
        'Artritis inflamatoria': {
          'G2': {
            corticoid: 'Prednisona (Dacortin®) 10-20 mg/día',
            management: 'AINEs. Infiltración intraarticular si oligoartritis. Derivar a Reumatología',
            monitoring: 'VSG, PCR, FR, anti-CCP. Ecografía articular',
            ici: 'Puede continuar',
            taper: 'Reducción progresiva. Considerar MTX si corticodependiente'
          },
          'G3': {
            corticoid: 'Prednisona (Dacortin®) 0.5-1 mg/kg/día',
            management: 'Considerar anti-IL6R (tocilizumab) o MTX si refractario',
            monitoring: 'Función articular. Ecografía',
            ici: 'Interrumpir temporalmente',
            taper: '6-8 semanas'
          }
        },
        'Miositis': {
          'G2': {
            corticoid: 'Prednisona (Dacortin®) 0.5-1 mg/kg/día',
            management: 'Descartar miopatía necrotizante. Ac anti-miositis. RM muscular',
            monitoring: 'CK, troponina T (músculo), LDH. ECG (descartar miocarditis)',
            ici: 'Interrumpir',
            taper: '6-8 semanas'
          },
          'G3': {
            corticoid: 'Metilprednisolona (Urbason®) 1-2 mg/kg/día + IGIV',
            management: 'Si síntomas bulbares: IGIV 2 g/kg. Descartar miocarditis (troponina I)',
            monitoring: 'CK diaria. Fuerza muscular. Disfagia',
            ici: 'Suspender',
            taper: 'Muy prolongado'
          }
        }
      },
      'Renal': {
        'Nefritis intersticial aguda': {
          'G1': {
            corticoid: 'No indicado',
            labValues: 'Creatinina: 1.5-2× basal, o FG 50-80 ml/min',
            management: 'Suspender nefrotóxicos. Monitorización estrecha',
            monitoring: 'Creatinina, iones, sedimento cada 2-3 días',
            ici: 'Continuar con precaución'
          },
          'G2': {
            corticoid: 'Prednisona (Dacortin®) 1 mg/kg/día',
            labValues: 'Creatinina: 2-3× basal, o FG 25-50 ml/min (KDIGO 2)',
            management: 'Suspender nefrotóxicos (AINEs, IBP). Considerar biopsia renal',
            monitoring: 'Creatinina, iones, sedimento urinario',
            ici: 'Interrumpir temporalmente',
            taper: '8-12 semanas (taper lento por alto riesgo de recaída)'
          },
          'G3': {
            corticoid: 'Metilprednisolona (Urbason®) 250-500 mg IV x 3 días',
            labValues: 'Creatinina: >3× basal, o FG <25 ml/min (KDIGO 3)',
            management: 'Biopsia renal. Si refractario: MMF, ciclofosfamida o rituximab',
            monitoring: 'Función renal diaria. Considerar diálisis',
            ici: 'Suspender',
            taper: '8-12 semanas'
          },
          'G4': {
            corticoid: 'Metilprednisolona (Urbason®) 500-1000 mg IV x 3 días',
            labValues: 'Insuficiencia renal aguda que requiere diálisis',
            management: 'UCI. Diálisis de urgencia. Inmunosupresión 2ª línea precoz',
            monitoring: 'Diálisis. Función renal horaria',
            ici: 'Suspender permanentemente',
            taper: 'Muy prolongado'
          }
        }
      },
      'Hematológico': {
        'Anemia hemolítica autoinmune': {
          'G1': {
            corticoid: 'No indicado inicialmente',
            labValues: 'Hemoglobina: 10-12 g/dl, Coombs directo positivo',
            management: 'Monitorización. Ácido fólico. Descartar otras causas',
            monitoring: 'Hemoglobina, reticulocitos, bilirrubina, LDH',
            ici: 'Puede continuar con precaución'
          },
          'G2': {
            corticoid: 'Prednisona (Dacortin®) 1 mg/kg/día',
            labValues: 'Hemoglobina: 8-10 g/dl, Reticulocitos elevados, Haptoglobina baja',
            management: 'Test de Coombs. Transfusión si precisa. Ácido fólico',
            monitoring: 'Hemoglobina, reticulocitos, bilirrubina, LDH, haptoglobina',
            ici: 'Interrumpir',
            taper: '6-8 semanas'
          },
          'G3': {
            corticoid: 'Metilprednisolona (Urbason®) 1-2 mg/kg/día + IGIV o Rituximab',
            labValues: 'Hemoglobina: <8 g/dl, Hemólisis severa',
            management: 'IGIV 1 g/kg/día x 2 días. Rituximab si refractario',
            monitoring: 'Hemograma diario',
            ici: 'Suspender',
            taper: 'Prolongado'
          },
          'G4': {
            corticoid: 'Metilprednisolona (Urbason®) 2 mg/kg/día IV + IGIV + Rituximab',
            labValues: 'Hemoglobina: <6.5 g/dl, Compromiso vital',
            management: 'UCI. Transfusión urgente. IGIV + Rituximab inmediato',
            monitoring: 'Hemograma cada 6h. Soporte transfusional',
            ici: 'Suspender permanentemente',
            taper: 'Muy prolongado'
          }
        },
        'Trombocitopenia': {
          'G1': {
            corticoid: 'No indicado',
            labValues: 'Plaquetas: 75,000-150,000/μl',
            management: 'Monitorización. Descartar otras causas',
            monitoring: 'Plaquetas 2x/semana',
            ici: 'Continuar con precaución'
          },
          'G2': {
            corticoid: 'Prednisona (Dacortin®) 1 mg/kg/día',
            labValues: 'Plaquetas: 50,000-75,000/μl',
            management: 'Descartar causas centrales (biopsia MO). IGIV si sangrado',
            monitoring: 'Plaquetas 2-3x/semana',
            ici: 'Interrumpir',
            taper: '6-8 semanas'
          },
          'G3': {
            corticoid: 'Metilprednisolona (Urbason®) 1-2 mg/kg/día + IGIV',
            labValues: 'Plaquetas: 25,000-50,000/μl',
            management: 'IGIV 1 g/kg/día x 2. Si refractario: eltrombopag (agonista TPO)',
            monitoring: 'Plaquetas diarias. Vigilar sangrado',
            ici: 'Suspender',
            taper: 'Prolongado'
          },
          'G4': {
            corticoid: 'Metilprednisolona (Urbason®) 2 mg/kg/día IV + IGIV urgente',
            labValues: 'Plaquetas: <25,000/μl con sangrado activo',
            management: 'UCI. IGIV 1-2 g/kg urgente. Transfusión plaquetaria. Considerar rituximab',
            monitoring: 'Plaquetas cada 6h. Control estricto de sangrado',
            ici: 'Suspender permanentemente',
            taper: 'Muy prolongado'
          }
        },
        'Neutropenia': {
          'G1': {
            corticoid: 'No indicado',
            labValues: 'Neutrófilos: 1,500-2,000/μl',
            management: 'Monitorización. Evitar infecciones',
            monitoring: 'Hemograma 2x/semana',
            ici: 'Continuar con precaución'
          },
          'G2': {
            corticoid: 'Prednisona (Dacortin®) 1 mg/kg/día si persistente',
            labValues: 'Neutrófilos: 1,000-1,500/μl',
            management: 'Biopsia médula ósea. G-CSF si indicado',
            monitoring: 'Hemograma diario. Vigilar fiebre',
            ici: 'Interrumpir temporalmente',
            taper: '6-8 semanas'
          },
          'G3': {
            corticoid: 'Metilprednisolona (Urbason®) 1-2 mg/kg/día',
            labValues: 'Neutrófilos: 500-1,000/μl',
            management: 'Hospitalización. G-CSF. Profilaxis antibiótica',
            monitoring: 'Hemograma diario. Temperatura cada 4h',
            ici: 'Suspender',
            taper: 'Prolongado'
          },
          'G4': {
            corticoid: 'Metilprednisolona (Urbason®) 2 mg/kg/día IV',
            labValues: 'Neutrófilos: <500/μl',
            management: 'UCI. G-CSF diario. Antibióticos empíricos si fiebre. Aislamiento',
            monitoring: 'Hemograma cada 12h. Cultivos seriados',
            ici: 'Suspender permanentemente',
            taper: 'Muy prolongado'
          }
        },
        'Linfohistiocitosis hemofagocítica': {
          'G4': {
            corticoid: 'Dexametasona (Fortecortin®) según protocolo HLH + Tocilizumab',
            labValues: 'Ferritina: >10,000 ng/ml, Triglicéridos: >265 mg/dl, Fibrinógeno: <150 mg/dl, Citopenia ≥2 líneas',
            management: 'UCI. Tocilizumab 8 mg/kg. Etopósido si refractario. Considerar ruxolitinib',
            monitoring: 'Ferritina, triglicéridos, fibrinógeno. MO con hemofagocitosis',
            ici: 'Suspender permanentemente',
            taper: 'Según protocolo HLH'
          }
        }
      }
    };

    const organRecs = recommendations[selectedOrgan];
    if (!organRecs) return getGenericRecommendation();
    
    const toxRecs = organRecs[selectedToxicity];
    if (!toxRecs) return getGenericRecommendation();
    
    const gradeRec = toxRecs[selectedGrade];
    return gradeRec || getGenericRecommendation();
  };

  const getGenericRecommendation = () => {
    const generic = {
      'G1': {
        corticoid: 'No indicado habitualmente',
        management: 'Tratamiento sintomático. Monitorización estrecha',
        monitoring: 'Control semanal',
        ici: 'Continuar con precaución'
      },
      'G2': {
        corticoid: 'Prednisona (Dacortin®) 0.5-1 mg/kg/día',
        management: 'Valorar causa alternativa. Tratamiento específico de órgano',
        monitoring: 'Control 2-3x/semana',
        ici: 'Interrumpir temporalmente',
        taper: '4-6 semanas'
      },
      'G3': {
        corticoid: 'Prednisona (Dacortin®) 1-2 mg/kg/día o Metilprednisolona IV',
        management: 'Hospitalización. Consultar especialista. 2ª línea si no respuesta en 48-72h',
        monitoring: 'Según órgano afectado',
        ici: 'Suspender',
        taper: '6-8 semanas'
      },
      'G4': {
        corticoid: 'Metilprednisolona (Urbason®) 1000 mg IV/día',
        management: 'UCI. Inmunosupresión de 2ª línea precoz',
        monitoring: 'Monitorización intensiva',
        ici: 'Suspender permanentemente',
        taper: 'Prolongado e individualizado'
      }
    };
    
    return generic[selectedGrade];
  };

  const getLabValuesByGrade = (grade) => {
    // Primero intentamos obtener la recomendación completa
    const fullRec = getDetailedRecommendation();
    if (fullRec && fullRec.labValues) {
      // Si estamos buscando el grado actual seleccionado
      if (grade === selectedGrade) {
        return fullRec.labValues;
      }
    }
    
    // Si no, buscamos directamente en las recomendaciones
    // Esta es una búsqueda simplificada - en producción usaríamos la misma estructura
    return null;
  };

  const calculateTotalDose = () => {
    const b = parseFloat(currentDose.breakfast) || 0;
    const l = parseFloat(currentDose.lunch) || 0;
    const d = parseFloat(currentDose.dinner) || 0;
    return b + l + d;
  };

  const calculateDoseByWeight = () => {
    if (!patientWeight) return null;
    const weight = parseFloat(patientWeight);
    return {
      low: Math.round(weight * 0.5 * 2) / 2,
      mid: Math.round(weight * 1 * 2) / 2,
      high: Math.round(weight * 2 * 2) / 2
    };
  };

  const findClosestDose = (targetDose, presentations) => {
    if (targetDose <= 0) return { total: 0, pills: [] };
    
    let bestCombination = { total: 0, pills: [] };
    let minDiff = Math.abs(targetDose);

    for (let p1 of presentations) {
      for (let n1 = 0; n1 <= 4; n1++) {
        for (let p2 of presentations) {
          for (let n2 = 0; n2 <= 3; n2++) {
            if (n1 + n2 > 4) continue;
            const total = n1 * p1 + n2 * p2;
            const diff = Math.abs(total - targetDose);
            if (diff < minDiff && total <= targetDose + 2.5) {
              minDiff = diff;
              const pills = [];
              if (n1 > 0) pills.push(`${n1}×${p1}mg`);
              if (n2 > 0) pills.push(`${n2}×${p2}mg`);
              bestCombination = { total, pills };
            }
          }
        }
      }
    }

    return bestCombination;
  };

  const distributeDose = (totalDose, corticoidType) => {
    if (totalDose <= 0) {
      return {
        breakfast: { total: 0, pills: [] },
        lunch: { total: 0, pills: [] },
        dinner: { total: 0, pills: [] },
        actualTotal: 0
      };
    }

    const presentations = corticoidEquivalence[corticoidType].presentations;
    
    // Distribución preferente: priorizar desayuno y comida, minimizar cena
    // Desayuno: 50%, Comida: 30-40%, Cena: 10-20%
    let breakfast = totalDose * 0.5;
    let lunch = totalDose * 0.35;
    let dinner = totalDose * 0.15;

    const breakfastDose = findClosestDose(breakfast, presentations);
    const remainingAfterBreakfast = totalDose - breakfastDose.total;
    
    // De lo que queda, distribuir 70% comida, 30% cena
    const lunchTarget = remainingAfterBreakfast * 0.7;
    const lunchDose = findClosestDose(lunchTarget, presentations);
    
    const dinnerDose = findClosestDose(totalDose - breakfastDose.total - lunchDose.total, presentations);

    return {
      breakfast: breakfastDose,
      lunch: lunchDose,
      dinner: dinnerDose,
      actualTotal: breakfastDose.total + lunchDose.total + dinnerDose.total
    };
  };

  const calculateTaperSchedule = () => {
    const startDose = calculateTotalDose();
    const weeks = parseInt(weeksToTaper);
    const reduction = parseFloat(weeklyReduction);

    if (!startDose || !weeks || !reduction) {
      alert('Por favor completa todos los campos');
      return;
    }

    const schedule = [];
    let currentWeekDose = startDose;

    for (let week = 0; week < weeks; week++) {
      const weekDose = Math.max(0, currentWeekDose - (week * reduction));
      
      if (weekDose <= 0 && week > 0) break;
      
      const prednisonaDist = distributeDose(weekDose, 'prednisona');
      
      const metilDose = weekDose * corticoidEquivalence.metilprednisolona.factor;
      const metilDist = distributeDose(metilDose, 'metilprednisolona');
      
      const dexaDose = weekDose * corticoidEquivalence.dexametasona.factor;
      const dexaDist = distributeDose(dexaDose, 'dexametasona');

      schedule.push({
        week: week + 1,
        targetDose: weekDose,
        prednisona: prednisonaDist,
        metilprednisolona: metilDist,
        dexametasona: dexaDist
      });
    }

    setTaperSchedule(schedule);
  };

  const generatePDF = async () => {
    if (!taperSchedule) return;
    
    // Verificar que jsPDF esté disponible
    if (!window.jspdf) {
      alert('Las librerías de generación aún se están cargando. Por favor, espera unos segundos e intenta de nuevo.');
      return;
    }
    
    try {
      // Crear PDF usando jsPDF (disponible vía CDN)
      const { jsPDF } = window.jspdf;
      const doc = new jsPDF();
      
      let yPos = 20;
      const pageWidth = doc.internal.pageSize.getWidth();
      const margin = 20;
      const contentWidth = pageWidth - 2 * margin;
      
      // Título
      doc.setFontSize(18);
      doc.setTextColor(30, 64, 175);
      doc.text('CALENDARIO DE DESCENSO DE CORTICOIDES', pageWidth / 2, yPos, { align: 'center' });
      yPos += 10;
      
      // Subtítulo
      doc.setFontSize(14);
      doc.setTextColor(124, 58, 237);
      const corticoidName = corticoidEquivalence[selectedCorticoid].name;
      const commercialName = corticoidEquivalence[selectedCorticoid].commercial;
      doc.text(`${corticoidName} (${commercialName})`, pageWidth / 2, yPos, { align: 'center' });
      yPos += 8;
      
      // Presentaciones
      doc.setFontSize(9);
      doc.setTextColor(0, 0, 0);
      const presentations = corticoidEquivalence[selectedCorticoid].availableDoses;
      doc.text(presentations, pageWidth / 2, yPos, { align: 'center' });
      yPos += 6;
      
      // Fecha
      doc.text(`Fecha: ${new Date().toLocaleDateString('es-ES')}`, pageWidth / 2, yPos, { align: 'center' });
      yPos += 15;
      
      // Calendario semanal
      taperSchedule.forEach((week, index) => {
        const dist = week[selectedCorticoid];
        
        // Nueva página si no hay espacio
        if (yPos > 250) {
          doc.addPage();
          yPos = 20;
        }
        
        // Título de semana
        doc.setFontSize(12);
        doc.setTextColor(124, 58, 237);
        doc.text(`Semana ${week.week}`, margin, yPos);
        yPos += 8;
        
        // Tabla de dosis
        doc.setFontSize(10);
        doc.setTextColor(0, 0, 0);
        
        const tableData = [
          ['🌅 Desayuno', `${dist.breakfast.total} mg`, dist.breakfast.pills.join(' + ') || 'Sin toma'],
          ['☀️ Comida', `${dist.lunch.total} mg`, dist.lunch.pills.join(' + ') || 'Sin toma'],
          ['🌙 Cena', `${dist.dinner.total} mg`, dist.dinner.pills.join(' + ') || 'Sin toma'],
          ['TOTAL', `${dist.actualTotal} mg`, '']
        ];
        
        tableData.forEach((row, i) => {
          const bg = i === 3 ? [219, 234, 254] : [243, 244, 246];
          doc.setFillColor(...bg);
          doc.rect(margin, yPos, contentWidth, 8, 'F');
          
          doc.text(row[0], margin + 2, yPos + 5);
          doc.text(row[1], margin + 40, yPos + 5);
          doc.text(row[2], margin + 70, yPos + 5);
          yPos += 8;
        });
        
        yPos += 5;
      });
      
      // Nueva página para advertencias
      doc.addPage();
      yPos = 20;
      
      // Título advertencias
      doc.setFontSize(14);
      doc.setTextColor(220, 38, 38);
      doc.text('⚠️ INFORMACIÓN IMPORTANTE', pageWidth / 2, yPos, { align: 'center' });
      yPos += 12;
      
      // Profilaxis
      doc.setFontSize(11);
      doc.setTextColor(0, 0, 0);
      doc.text('Tratamiento Profiláctico Obligatorio:', margin, yPos);
      yPos += 8;
      
      doc.setFontSize(9);
      const warnings = [
        '🛡️ Omeprazol 20-40 mg/día durante TODO el tratamiento',
        '🦠 Septrim Forte: Lunes-Miércoles-Viernes (si ≥20mg/día >4 semanas)',
        '🦴 Calcio 1200 mg/día + Vitamina D 800-2000 UI/día'
      ];
      
      warnings.forEach(w => {
        doc.text(w, margin + 5, yPos);
        yPos += 6;
      });
      
      yPos += 8;
      
      // Advertencias críticas
      doc.setFontSize(11);
      doc.setTextColor(220, 38, 38);
      doc.text('❌ NUNCA suspender bruscamente', margin, yPos);
      yPos += 6;
      doc.setFontSize(9);
      doc.setTextColor(0, 0, 0);
      doc.text('Riesgo de insuficiencia suprarrenal aguda', margin + 5, yPos);
      yPos += 12;
      
      // Autoría
      doc.setFontSize(10);
      doc.setTextColor(0, 0, 0);
      doc.text('Elaborado por: Dr. Joaquín Gimeno', pageWidth / 2, yPos, { align: 'center' });
      yPos += 6;
      doc.setFontSize(9);
      doc.text('Basado en guías ESMO 2022 y NCCN 2026', pageWidth / 2, yPos, { align: 'center' });
      yPos += 10;
      
      // Disclaimer
      doc.setFontSize(8);
      doc.setTextColor(220, 38, 38);
      const disclaimer = 'IMPORTANTE: La información aquí contenida debe ser corroborada y confirmada por un médico con experiencia en el manejo de las toxicidades inmunomediadas.';
      const lines = doc.splitTextToSize(disclaimer, contentWidth);
      doc.text(lines, pageWidth / 2, yPos, { align: 'center' });
      
      // Descargar
      doc.save(`calendario_descenso_${selectedCorticoid}.pdf`);
      
    } catch (error) {
      console.error('Error generando PDF:', error);
      alert('Error al generar el PDF. Asegúrate de que jsPDF esté cargado.');
    }
  };

  const generateWordDoc = async () => {
    if (!taperSchedule) return;
    
    // Verificar que docx esté disponible
    if (!window.docx) {
      alert('Las librerías de generación aún se están cargando. Por favor, espera unos segundos e intenta de nuevo.');
      return;
    }
    
    try {
      // Importar docx desde CDN
      const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, AlignmentType, WidthType } = window.docx;
      
      const corticoidName = corticoidEquivalence[selectedCorticoid].name;
      const commercialName = corticoidEquivalence[selectedCorticoid].commercial;
      const presentations = corticoidEquivalence[selectedCorticoid].availableDoses;
      
      // Crear párrafos del documento
      const children = [];
      
      // Título
      children.push(
        new Paragraph({
          text: 'CALENDARIO DE DESCENSO DE CORTICOIDES',
          heading: 'Heading1',
          alignment: AlignmentType.CENTER,
        })
      );
      
      // Subtítulo
      children.push(
        new Paragraph({
          text: `${corticoidName} (${commercialName})`,
          heading: 'Heading2',
          alignment: AlignmentType.CENTER,
        })
      );
      
      // Info
      children.push(
        new Paragraph({
          children: [
            new TextRun({ text: presentations, size: 20 })
          ],
          alignment: AlignmentType.CENTER,
        })
      );
      
      children.push(
        new Paragraph({
          children: [
            new TextRun({ text: `Fecha: ${new Date().toLocaleDateString('es-ES')}`, size: 20 })
          ],
          alignment: AlignmentType.CENTER,
        })
      );
      
      children.push(new Paragraph({ text: '' })); // Espacio
      
      // Calendario semanal
      taperSchedule.forEach(week => {
        const dist = week[selectedCorticoid];
        
        // Título semana
        children.push(
          new Paragraph({
            text: `Semana ${week.week}`,
            heading: 'Heading3',
          })
        );
        
        // Tabla
        const table = new Table({
          width: { size: 100, type: WidthType.PERCENTAGE },
          rows: [
            new TableRow({
              children: [
                new TableCell({ children: [new Paragraph('Toma')] }),
                new TableCell({ children: [new Paragraph('Dosis')] }),
                new TableCell({ children: [new Paragraph('Comprimidos')] }),
              ],
            }),
            new TableRow({
              children: [
                new TableCell({ children: [new Paragraph('🌅 Desayuno')] }),
                new TableCell({ children: [new Paragraph(`${dist.breakfast.total} mg`)] }),
                new TableCell({ children: [new Paragraph(dist.breakfast.pills.join(' + ') || 'Sin toma')] }),
              ],
            }),
            new TableRow({
              children: [
                new TableCell({ children: [new Paragraph('☀️ Comida')] }),
                new TableCell({ children: [new Paragraph(`${dist.lunch.total} mg`)] }),
                new TableCell({ children: [new Paragraph(dist.lunch.pills.join(' + ') || 'Sin toma')] }),
              ],
            }),
            new TableRow({
              children: [
                new TableCell({ children: [new Paragraph('🌙 Cena')] }),
                new TableCell({ children: [new Paragraph(`${dist.dinner.total} mg`)] }),
                new TableCell({ children: [new Paragraph(dist.dinner.pills.join(' + ') || 'Sin toma')] }),
              ],
            }),
            new TableRow({
              children: [
                new TableCell({ children: [new Paragraph({ text: 'TOTAL', bold: true })] }),
                new TableCell({ children: [new Paragraph({ text: `${dist.actualTotal} mg`, bold: true })] }),
                new TableCell({ children: [new Paragraph('')] }),
              ],
            }),
          ],
        });
        
        children.push(table);
        children.push(new Paragraph({ text: '' })); // Espacio
      });
      
      // Advertencias
      children.push(new Paragraph({ text: '', pageBreakBefore: true }));
      children.push(
        new Paragraph({
          text: '⚠️ INFORMACIÓN IMPORTANTE',
          heading: 'Heading1',
          alignment: AlignmentType.CENTER,
        })
      );
      
      children.push(
        new Paragraph({
          text: 'Tratamiento Profiláctico Obligatorio:',
          heading: 'Heading2',
        })
      );
      
      children.push(new Paragraph('🛡️ Omeprazol 20-40 mg/día durante TODO el tratamiento'));
      children.push(new Paragraph('🦠 Septrim Forte: Lunes-Miércoles-Viernes (si ≥20mg/día >4 semanas)'));
      children.push(new Paragraph('🦴 Calcio 1200 mg/día + Vitamina D 800-2000 UI/día'));
      children.push(new Paragraph({ text: '' }));
      
      children.push(
        new Paragraph({
          text: '❌ NUNCA suspender bruscamente',
          heading: 'Heading2',
        })
      );
      children.push(new Paragraph('Riesgo de insuficiencia suprarrenal aguda'));
      children.push(new Paragraph({ text: '' }));
      
      // Autoría
      children.push(
        new Paragraph({
          children: [new TextRun({ text: 'Elaborado por: Dr. Joaquín Gimeno', bold: true })],
          alignment: AlignmentType.CENTER,
        })
      );
      children.push(
        new Paragraph({
          text: 'Basado en guías ESMO 2022 y NCCN 2026',
          alignment: AlignmentType.CENTER,
        })
      );
      children.push(new Paragraph({ text: '' }));
      
      // Disclaimer
      children.push(
        new Paragraph({
          children: [
            new TextRun({
              text: 'IMPORTANTE: La información aquí contenida debe ser corroborada y confirmada por un médico con experiencia en el manejo de las toxicidades inmunomediadas.',
              italics: true,
              color: 'DC2626',
            })
          ],
          alignment: AlignmentType.CENTER,
        })
      );
      
      // Crear documento
      const doc = new Document({
        sections: [{
          children: children,
        }],
      });
      
      // Generar y descargar
      Packer.toBlob(doc).then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `calendario_descenso_${selectedCorticoid}.docx`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      });
      
    } catch (error) {
      console.error('Error generando Word:', error);
      alert('Error al generar el documento Word. Asegúrate de que docx esté cargado.');
    }
  };

  const renderToxicityRecommendations = () => {
    const recommendation = getDetailedRecommendation();
    
    return (
      <div className="space-y-6">
        <div className="flex items-center gap-3 mb-4">
          <Info className="text-blue-600" size={32} />
          <h2 className="text-2xl font-bold text-blue-700">Recomendaciones por Toxicidad Inmunomediada</h2>
        </div>
        
        <div className="space-y-4">
          <div className="bg-gradient-to-r from-blue-50 to-blue-100 p-4 rounded-lg border-2 border-blue-300">
            <label className="block font-semibold mb-2 text-blue-900">
              📋 Paso 1: Selecciona el órgano/sistema afectado
            </label>
            <select 
              className="w-full p-3 border-2 border-blue-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              value={selectedOrgan}
              onChange={(e) => {
                setSelectedOrgan(e.target.value);
                setSelectedToxicity('');
                setSelectedGrade('');
                setShowCorticoidRecommendation(false);
              }}
            >
              <option value="">-- Selecciona un órgano/sistema --</option>
              {Object.keys(organSystems).map(organ => (
                <option key={organ} value={organ}>{organ}</option>
              ))}
            </select>
          </div>

          {selectedOrgan && (
            <div className="bg-gradient-to-r from-purple-50 to-purple-100 p-4 rounded-lg border-2 border-purple-300">
              <label className="block font-semibold mb-2 text-purple-900">
                🔍 Paso 2: Especifica el tipo de toxicidad
              </label>
              <select 
                className="w-full p-3 border-2 border-purple-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                value={selectedToxicity}
                onChange={(e) => {
                  setSelectedToxicity(e.target.value);
                  setSelectedGrade('');
                  setShowCorticoidRecommendation(false);
                }}
              >
                <option value="">-- Selecciona el tipo específico --</option>
                {organSystems[selectedOrgan].map(tox => (
                  <option key={tox} value={tox}>{tox}</option>
                ))}
              </select>
            </div>
          )}

          {selectedToxicity && (
            <div className="bg-gradient-to-r from-orange-50 to-orange-100 p-4 rounded-lg border-2 border-orange-300">
              <label className="block font-semibold mb-3 text-orange-900">
                ⚠️ Paso 3: Determina el grado de toxicidad (CTCAE v5.0)
              </label>
              <div className="space-y-3">
                {Object.entries(toxicityGrades).map(([grade, info]) => {
                  // Obtener valores de laboratorio para ESTE grado específico
                  // Necesitamos buscarlos directamente en las recomendaciones
                  let labValues = null;
                  
                  // Intentar obtener los valores de lab para este grado específico
                  if (selectedOrgan && selectedToxicity) {
                    // Hacemos una búsqueda temporal simulando selección de este grado
                    const tempRecommendations = {
                      'Hepático': {
                        'Hepatitis': {
                          'G1': { labValues: 'AST/ALT: 1-3× LSN' },
                          'G2': { labValues: 'AST/ALT: 3-5× LSN' },
                          'G3': { labValues: 'AST/ALT: 5-20× LSN, o Bilirrubina: 3-10× LSN' },
                          'G4': { labValues: 'AST/ALT: >20× LSN, o Bilirrubina: >10× LSN' }
                        }
                      },
                      'Renal': {
                        'Nefritis intersticial aguda': {
                          'G1': { labValues: 'Creatinina: 1.5-2× basal, o FG 50-80 ml/min' },
                          'G2': { labValues: 'Creatinina: 2-3× basal, o FG 25-50 ml/min (KDIGO 2)' },
                          'G3': { labValues: 'Creatinina: >3× basal, o FG <25 ml/min (KDIGO 3)' },
                          'G4': { labValues: 'Insuficiencia renal aguda que requiere diálisis' }
                        }
                      },
                      'Pancreático': {
                        'Pancreatitis': {
                          'G1': { labValues: 'Lipasa/Amilasa: 1-2× LSN, asintomático' },
                          'G2': { labValues: 'Lipasa/Amilasa: >2-5× LSN, dolor abdominal moderado' },
                          'G3': { labValues: 'Lipasa/Amilasa: >5× LSN, dolor intenso, íleo' },
                          'G4': { labValues: 'Pancreatitis necrotizante, shock, fallo multiorgánico' }
                        },
                        'Elevación de lipasa asintomática': {
                          'G1': { labValues: 'Lipasa: 1-2× LSN, sin síntomas' },
                          'G2': { labValues: 'Lipasa: 2-5× LSN, sin dolor ni síntomas' }
                        }
                      },
                      'Hematológico': {
                        'Anemia hemolítica autoinmune': {
                          'G1': { labValues: 'Hemoglobina: 10-12 g/dl, Coombs directo positivo' },
                          'G2': { labValues: 'Hemoglobina: 8-10 g/dl, Reticulocitos elevados, Haptoglobina baja' },
                          'G3': { labValues: 'Hemoglobina: <8 g/dl, Hemólisis severa' },
                          'G4': { labValues: 'Hemoglobina: <6.5 g/dl, Compromiso vital' }
                        },
                        'Trombocitopenia': {
                          'G1': { labValues: 'Plaquetas: 75,000-150,000/μl' },
                          'G2': { labValues: 'Plaquetas: 50,000-75,000/μl' },
                          'G3': { labValues: 'Plaquetas: 25,000-50,000/μl' },
                          'G4': { labValues: 'Plaquetas: <25,000/μl con sangrado activo' }
                        },
                        'Neutropenia': {
                          'G1': { labValues: 'Neutrófilos: 1,500-2,000/μl' },
                          'G2': { labValues: 'Neutrófilos: 1,000-1,500/μl' },
                          'G3': { labValues: 'Neutrófilos: 500-1,000/μl' },
                          'G4': { labValues: 'Neutrófilos: <500/μl' }
                        },
                        'Linfohistiocitosis hemofagocítica': {
                          'G4': { labValues: 'Ferritina: >10,000 ng/ml, Triglicéridos: >265 mg/dl, Fibrinógeno: <150 mg/dl, Citopenia ≥2 líneas' }
                        }
                      }
                    };
                    
                    labValues = tempRecommendations[selectedOrgan]?.[selectedToxicity]?.[grade]?.labValues || null;
                  }
                  
                  return (
                    <div 
                      key={grade} 
                      className={`border-2 rounded-lg p-4 cursor-pointer transition-all ${
                        selectedGrade === grade 
                          ? 'bg-orange-200 border-orange-500 shadow-lg' 
                          : 'bg-white border-orange-200 hover:bg-orange-50'
                      }`}
                      onClick={() => {
                        setSelectedGrade(grade);
                        setShowCorticoidRecommendation(true);
                      }}
                    >
                      <label className="flex items-start cursor-pointer">
                        <input
                          type="radio"
                          name="grade"
                          value={grade}
                          checked={selectedGrade === grade}
                          onChange={() => {}}
                          className="mt-1 mr-3"
                        />
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <span className="font-bold text-xl text-orange-900">{grade}</span>
                            {grade === 'G4' && <AlertTriangle className="text-red-600" size={20} />}
                          </div>
                          <div className="text-sm text-gray-700 mb-1">
                            <strong>Descripción:</strong> {info.description}
                          </div>
                          <div className="text-sm text-blue-700 mb-2">
                            <strong>Acción ICI:</strong> {info.action}
                          </div>
                          {labValues && (
                            <div className="mt-3 bg-yellow-100 border-2 border-yellow-400 rounded-lg p-3">
                              <div className="flex items-start gap-2">
                                <span className="text-yellow-700 text-lg">🔬</span>
                                <div className="flex-1">
                                  <div className="font-semibold text-yellow-900 text-sm mb-1">
                                    Valores de Laboratorio:
                                  </div>
                                  <div className="text-sm text-gray-800 font-medium">
                                    {labValues}
                                  </div>
                                  <div className="text-xs text-gray-600 mt-1">
                                    LSN = Límite Superior de la Normalidad
                                  </div>
                                </div>
                              </div>
                            </div>
                          )}
                        </div>
                      </label>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {showCorticoidRecommendation && recommendation && (
            <div className="space-y-4">
              <Alert className="bg-gradient-to-r from-green-50 to-green-100 border-2 border-green-400">
                <AlertDescription>
                  <div className="space-y-4">
                    <div className="flex items-center gap-3">
                      <CheckCircle className="text-green-700" size={32} />
                      <h3 className="font-bold text-2xl text-green-800">
                        💊 Protocolo de Tratamiento
                      </h3>
                    </div>
                    
                    <div className="grid md:grid-cols-2 gap-4">
                      <div className="bg-white p-4 rounded-lg border-2 border-green-300">
                        <div className="font-semibold text-gray-600 mb-1">Toxicidad</div>
                        <div className="text-lg font-bold">{selectedToxicity}</div>
                        <div className="text-sm text-gray-600">{selectedOrgan}</div>
                      </div>
                      
                      <div className="bg-white p-4 rounded-lg border-2 border-green-300">
                        <div className="font-semibold text-gray-600 mb-1">Grado</div>
                        <div className="text-lg font-bold">{selectedGrade}</div>
                      </div>
                    </div>

                    <div className="bg-white p-5 rounded-lg border-3 border-green-500 shadow-lg">
                      <div className="flex items-center gap-2 mb-3">
                        <Pill className="text-green-700" size={24} />
                        <h4 className="font-bold text-lg text-green-900">Corticoides</h4>
                      </div>
                      <p className="text-xl font-bold text-green-900 mb-2">
                        {recommendation.corticoid}
                      </p>
                      {recommendation.taper && (
                        <p className="text-sm text-gray-600">
                          <strong>Duración descenso:</strong> {recommendation.taper}
                        </p>
                      )}
                    </div>

                    {recommendation.labValues && (
                      <div className="bg-yellow-50 p-4 rounded-lg border-2 border-yellow-400">
                        <h4 className="font-bold mb-2 text-yellow-900">🔬 Valores de Laboratorio ({selectedGrade})</h4>
                        <p className="text-sm font-semibold text-gray-800">{recommendation.labValues}</p>
                        <p className="text-xs text-gray-600 mt-1">LSN = Límite Superior de la Normalidad</p>
                      </div>
                    )}

                    <div className="bg-blue-50 p-4 rounded-lg border-2 border-blue-300">
                      <h4 className="font-bold mb-2 text-blue-900">📋 Manejo Adicional</h4>
                      <p className="text-sm">{recommendation.management}</p>
                    </div>

                    <div className="bg-purple-50 p-4 rounded-lg border-2 border-purple-300">
                      <h4 className="font-bold mb-2 text-purple-900">🔬 Monitorización</h4>
                      <p className="text-sm">{recommendation.monitoring}</p>
                    </div>

                    <div className="bg-orange-50 p-4 rounded-lg border-2 border-orange-300">
                      <h4 className="font-bold mb-2 text-orange-900">💉 Decisión sobre Inmunoterapia</h4>
                      <p className="text-sm font-semibold">{recommendation.ici}</p>
                    </div>
                  </div>
                </AlertDescription>
              </Alert>

              <div className="bg-gray-100 p-4 rounded-lg border-2 border-gray-300">
                <button
                  onClick={() => setShowAdditionalInfo(!showAdditionalInfo)}
                  className="w-full flex items-center justify-between font-semibold text-gray-800 hover:text-gray-900"
                >
                  <span>📊 Tabla de equivalencias entre corticoides</span>
                  <span>{showAdditionalInfo ? '▼' : '▶'}</span>
                </button>
                
                {showAdditionalInfo && (
                  <div className="mt-4 space-y-2 text-sm">
                    <div className="bg-white p-3 rounded">
                      <strong>Prednisona 5 mg</strong> = Metilprednisolona 4 mg = Dexametasona 0.75 mg
                    </div>
                    <div className="bg-white p-3 rounded">
                      <strong>Prednisona 10 mg</strong> = Metilprednisolona 8 mg = Dexametasona 1.5 mg
                    </div>
                    <div className="bg-white p-3 rounded">
                      <strong>Prednisona 20 mg</strong> = Metilprednisolona 16 mg = Dexametasona 3 mg
                    </div>
                    <div className="bg-white p-3 rounded">
                      <strong>Prednisona 40 mg</strong> = Metilprednisolona 32 mg = Dexametasona 6 mg
                    </div>
                    <div className="bg-white p-3 rounded">
                      <strong>Prednisona 60 mg</strong> = Metilprednisolona 48 mg = Dexametasona 9 mg
                    </div>
                    
                    <div className="mt-4 bg-yellow-50 p-3 rounded border border-yellow-300">
                      <strong>Factor de conversión:</strong>
                      <ul className="mt-2 ml-4 list-disc">
                        <li>Prednisona → Metilprednisolona: <strong>×0.8</strong></li>
                        <li>Prednisona → Dexametasona: <strong>×0.15</strong></li>
                      </ul>
                    </div>
                  </div>
                )}
              </div>

              <Alert className="bg-red-50 border-2 border-red-400">
                <AlertDescription>
                  <div className="flex items-start gap-3">
                    <AlertTriangle className="text-red-600 flex-shrink-0 mt-1" size={24} />
                    <div>
                      <h4 className="font-bold text-red-800 mb-3 text-lg">
                        ⚠️ Tratamiento Profiláctico Concomitante OBLIGATORIO
                      </h4>
                      <div className="space-y-2 text-sm">
                        <div className="bg-white p-3 rounded border-l-4 border-red-500">
                          <strong className="text-red-800">🛡️ Protección gástrica:</strong>
                          <p className="mt-1">Omeprazol 20-40 mg/día (o Esomeprazol 20-40 mg/día) en ayunas</p>
                          <p className="text-xs text-gray-600 mt-1">Mantener durante todo el tratamiento corticoideo</p>
                        </div>
                        
                        <div className="bg-white p-3 rounded border-l-4 border-blue-500">
                          <strong className="text-blue-800">🦠 Profilaxis Pneumocystis jirovecii:</strong>
                          <p className="mt-1">Septrim Forte (800/160 mg) 1 comprimido: <strong>Lunes - Miércoles - Viernes</strong></p>
                          <p className="text-xs text-gray-600 mt-1">Iniciar si prednisona ≥20 mg/día durante >4 semanas</p>
                          <p className="text-xs text-red-600 mt-1">⚠️ Alternativa si alergia: Pentamidina inhalada o Dapsona</p>
                        </div>
                        
                        <div className="bg-white p-3 rounded border-l-4 border-green-500">
                          <strong className="text-green-800">🦴 Protección ósea:</strong>
                          <p className="mt-1">Calcio 1200 mg/día + Vitamina D 800-2000 UI/día</p>
                          <p className="text-xs text-gray-600 mt-1">Considerar densitometría ósea si tratamiento prolongado (>3 meses)</p>
                          <p className="text-xs text-gray-600 mt-1">Bifosfonatos si osteoporosis previa o alto riesgo de fractura</p>
                        </div>
                        
                        <div className="bg-white p-3 rounded border-l-4 border-orange-500">
                          <strong className="text-orange-800">📊 Monitorización adicional:</strong>
                          <ul className="mt-1 ml-4 list-disc text-xs space-y-1">
                            <li>Control glucemia (riesgo de diabetes esteroidea)</li>
                            <li>Presión arterial (riesgo de HTA)</li>
                            <li>Peso corporal (retención hídrica)</li>
                            <li>Signos de infección (inmunosupresión)</li>
                          </ul>
                        </div>

                        <div className="bg-yellow-50 p-3 rounded border-l-4 border-yellow-500 mt-3">
                          <strong className="text-yellow-800">⚠️ Educación al paciente:</strong>
                          <ul className="mt-1 ml-4 list-disc text-xs space-y-1">
                            <li>NO suspender corticoides bruscamente (riesgo de insuficiencia suprarrenal)</li>
                            <li>Llevar tarjeta de identificación de tratamiento con corticoides</li>
                            <li>Aumentar dosis en situaciones de estrés (fiebre, cirugía, trauma)</li>
                            <li>Consultar URGENTE si: fiebre, disnea, dolor torácico, síntomas neurológicos</li>
                          </ul>
                        </div>
                      </div>
                    </div>
                  </div>
                </AlertDescription>
              </Alert>
            </div>
          )}
        </div>
      </div>
    );
  };

  const renderDoseCalculator = () => (
    <div className="space-y-6">
      <div className="flex items-center gap-3 mb-4">
        <Calendar className="text-purple-600" size={32} />
        <h2 className="text-2xl font-bold text-purple-700">Calculadora de Descenso de Corticoides</h2>
      </div>
      
      <div className="space-y-4">
        {patientWeight && (
          <Alert className="bg-blue-50 border-blue-300">
            <AlertDescription>
              <div className="text-sm">
                <strong>Dosis orientativas de Prednisona según peso ({patientWeight} kg):</strong>
                <div className="mt-2 grid grid-cols-3 gap-2">
                  <div className="bg-white p-2 rounded">
                    <div className="text-xs text-gray-600">Baja dosis</div>
                    <div className="font-bold">{calculateDoseByWeight()?.low} mg/día</div>
                    <div className="text-xs text-gray-500">(0.5 mg/kg)</div>
                  </div>
                  <div className="bg-white p-2 rounded">
                    <div className="text-xs text-gray-600">Dosis media</div>
                    <div className="font-bold">{calculateDoseByWeight()?.mid} mg/día</div>
                    <div className="text-xs text-gray-500">(1 mg/kg)</div>
                  </div>
                  <div className="bg-white p-2 rounded">
                    <div className="text-xs text-gray-600">Dosis alta</div>
                    <div className="font-bold">{calculateDoseByWeight()?.high} mg/día</div>
                    <div className="text-xs text-gray-500">(2 mg/kg)</div>
                  </div>
                </div>
              </div>
            </AlertDescription>
          </Alert>
        )}

        <div className="bg-gradient-to-r from-purple-50 to-purple-100 p-5 rounded-lg border-2 border-purple-300">
          <h3 className="font-bold mb-3 text-purple-900">Peso del paciente (opcional)</h3>
          <input
            type="number"
            step="0.1"
            className="w-full p-3 border-2 border-purple-300 rounded-lg"
            value={patientWeight}
            onChange={(e) => setPatientWeight(e.target.value)}
            placeholder="Peso en kg (para cálculo orientativo)"
          />
        </div>

        <div className="bg-gradient-to-r from-blue-50 to-blue-100 p-5 rounded-lg border-2 border-blue-300">
          <h3 className="font-bold mb-3 text-blue-900">
            📊 Dosis Actual de Prednisona (mg)
          </h3>
          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="block text-sm mb-2 font-semibold">🌅 Desayuno</label>
              <input
                type="number"
                step="2.5"
                className="w-full p-3 border-2 border-blue-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                value={currentDose.breakfast}
                onChange={(e) => setCurrentDose({...currentDose, breakfast: e.target.value})}
                placeholder="0"
              />
            </div>
            <div>
              <label className="block text-sm mb-2 font-semibold">☀️ Comida</label>
              <input
                type="number"
                step="2.5"
                className="w-full p-3 border-2 border-blue-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                value={currentDose.lunch}
                onChange={(e) => setCurrentDose({...currentDose, lunch: e.target.value})}
                placeholder="0"
              />
            </div>
            <div>
              <label className="block text-sm mb-2 font-semibold">🌙 Cena</label>
              <input
                type="number"
                step="2.5"
                className="w-full p-3 border-2 border-blue-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                value={currentDose.dinner}
                onChange={(e) => setCurrentDose({...currentDose, dinner: e.target.value})}
                placeholder="0"
              />
            </div>
          </div>
          <div className="mt-4 p-4 bg-white rounded-lg border-2 border-blue-400">
            <div className="text-center">
              <div className="text-sm text-gray-600 mb-1">Dosis Total Diaria</div>
              <div className="text-3xl font-bold text-blue-900">
                {calculateTotalDose()} mg
              </div>
            </div>
          </div>
        </div>

        <div className="grid md:grid-cols-2 gap-4">
          <div className="bg-gradient-to-r from-orange-50 to-orange-100 p-4 rounded-lg border-2 border-orange-300">
            <label className="block font-semibold mb-2 text-orange-900">
              ⏱️ Tiempo de descenso (semanas)
            </label>
            <input
              type="number"
              className="w-full p-3 border-2 border-orange-300 rounded-lg focus:ring-2 focus:ring-orange-500"
              value={weeksToTaper}
              onChange={(e) => setWeeksToTaper(e.target.value)}
              placeholder="Ej: 6"
            />
            <p className="text-xs text-gray-600 mt-2">
              💡 Recomendado: G2: 4-6 semanas | G3: 6-8 semanas | G4: ≥8 semanas
            </p>
          </div>
          
          <div className="bg-gradient-to-r from-green-50 to-green-100 p-4 rounded-lg border-2 border-green-300">
            <label className="block font-semibold mb-2 text-green-900">
              📉 Reducción semanal (mg/semana)
            </label>
            <input
              type="number"
              step="2.5"
              className="w-full p-3 border-2 border-green-300 rounded-lg focus:ring-2 focus:ring-green-500"
              value={weeklyReduction}
              onChange={(e) => setWeeklyReduction(e.target.value)}
              placeholder="Ej: 5 o 10"
            />
            <p className="text-xs text-gray-600 mt-2">
              💡 Habitual: 5-10 mg/semana. Más lento si >20 mg o toxicidad grave
            </p>
          </div>
        </div>

        <button
          onClick={calculateTaperSchedule}
          className="w-full bg-gradient-to-r from-purple-600 to-purple-700 text-white p-4 rounded-lg font-bold text-lg hover:from-purple-700 hover:to-purple-800 transition-all shadow-lg"
        >
          🧮 Calcular Calendario de Descenso
        </button>

        {taperSchedule && (
          <div className="space-y-4">
            <div className="bg-gradient-to-r from-indigo-50 to-indigo-100 p-4 rounded-lg border-2 border-indigo-300">
              <label className="block font-semibold mb-2 text-indigo-900">
                💊 Mostrar calendario para:
              </label>
              <select 
                className="w-full p-3 border-2 border-indigo-300 rounded-lg focus:ring-2 focus:ring-indigo-500 text-lg"
                value={selectedCorticoid}
                onChange={(e) => setSelectedCorticoid(e.target.value)}
              >
                <option value="prednisona">
                  Prednisona - {corticoidEquivalence.prednisona.commercial}
                </option>
                <option value="metilprednisolona">
                  Metilprednisolona - {corticoidEquivalence.metilprednisolona.commercial}
                </option>
                <option value="dexametasona">
                  Dexametasona - {corticoidEquivalence.dexametasona.commercial}
                </option>
              </select>
            </div>

            <Alert className="bg-gradient-to-r from-purple-50 to-purple-100 border-2 border-purple-400">
              <AlertDescription>
                <div className="space-y-3">
                  <div className="flex items-center gap-3 mb-4">
                    <Calendar className="text-purple-700" size={28} />
                    <h3 className="font-bold text-xl text-purple-800">
                      📅 Calendario de Descenso Personalizado
                    </h3>
                  </div>
                  
                  <div className="bg-white p-3 rounded-lg border-2 border-purple-300 mb-4">
                    <div className="text-center">
                      <div className="text-sm text-gray-600">Corticoide seleccionado</div>
                      <div className="text-xl font-bold text-purple-900">
                        {corticoidEquivalence[selectedCorticoid].commercial}
                      </div>
                      <div className="text-sm text-gray-600">
                        ({corticoidEquivalence[selectedCorticoid].name})
                      </div>
                      <div className="text-xs text-gray-500 mt-2">
                        {corticoidEquivalence[selectedCorticoid].availableDoses}
                      </div>
                    </div>
                  </div>

                  <div className="space-y-3">
                    {taperSchedule.map((week, index) => {
                      const dist = week[selectedCorticoid];
                      const isLastWeek = index === taperSchedule.length - 1;
                      
                      return (
                        <div 
                          key={week.week} 
                          className={`bg-white p-5 rounded-lg border-3 ${
                            isLastWeek 
                              ? 'border-green-400 bg-green-50' 
                              : 'border-purple-300'
                          } shadow-md hover:shadow-lg transition-shadow`}
                        >
                          <div className="flex items-center justify-between mb-3">
                            <div className="font-bold text-lg text-purple-800">
                              📆 Semana {week.week}
                            </div>
                            {isLastWeek && (
                              <span className="bg-green-500 text-white px-3 py-1 rounded-full text-xs font-bold">
                                ÚLTIMA SEMANA
                              </span>
                            )}
                          </div>
                          
                          <div className="grid grid-cols-3 gap-3 mb-3">
                            <div className="bg-gradient-to-br from-yellow-50 to-yellow-100 p-3 rounded-lg border-2 border-yellow-300">
                              <div className="font-semibold text-sm mb-1">🌅 Desayuno</div>
                              <div className="text-xs text-gray-600 mb-2 min-h-[2.5rem]">
                                {dist.breakfast.pills.join(' + ') || 'Sin toma'}
                              </div>
                              <div className="font-bold text-lg text-yellow-900">
                                {dist.breakfast.total} mg
                              </div>
                            </div>
                            
                            <div className="bg-gradient-to-br from-orange-50 to-orange-100 p-3 rounded-lg border-2 border-orange-300">
                              <div className="font-semibold text-sm mb-1">☀️ Comida</div>
                              <div className="text-xs text-gray-600 mb-2 min-h-[2.5rem]">
                                {dist.lunch.pills.join(' + ') || 'Sin toma'}
                              </div>
                              <div className="font-bold text-lg text-orange-900">
                                {dist.lunch.total} mg
                              </div>
                            </div>
                            
                            <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-3 rounded-lg border-2 border-blue-300">
                              <div className="font-semibold text-sm mb-1">🌙 Cena</div>
                              <div className="text-xs text-gray-600 mb-2 min-h-[2.5rem]">
                                {dist.dinner.pills.join(' + ') || 'Sin toma'}
                              </div>
                              <div className="font-bold text-lg text-blue-900">
                                {dist.dinner.total} mg
                              </div>
                            </div>
                          </div>
                          
                          <div className="mt-3 pt-3 border-t-2 border-gray-200 text-center">
                            <span className="text-sm text-gray-600 mr-2">Total día:</span>
                            <span className="font-bold text-xl text-purple-900">
                              {dist.actualTotal} mg
                            </span>
                          </div>
                        </div>
                      );
                    })}
                  </div>

                  <div className="bg-yellow-50 p-4 rounded-lg border-2 border-yellow-300 mt-4">
                    <div className="flex items-start gap-2">
                      <Info className="text-yellow-700 flex-shrink-0 mt-1" size={20} />
                      <div className="text-sm">
                        <strong className="text-yellow-900">Nota importante:</strong>
                        <p className="mt-1 text-gray-700">
                          Las dosis mostradas son aproximaciones basadas en las presentaciones comerciales disponibles.
                          Ajusta según criterio clínico y respuesta del paciente.
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="bg-gradient-to-r from-blue-50 to-blue-100 p-4 rounded-lg border-2 border-blue-300 mt-4">
                    <h4 className="font-bold text-blue-900 mb-3">📄 Exportar Calendario</h4>
                    <p className="text-sm text-gray-700 mb-4">
                      Descarga el calendario de descenso para compartir con el paciente o editar según necesites
                    </p>
                    {!librariesLoaded && (
                      <p className="text-xs text-orange-600 mb-3">
                        ⏳ Cargando librerías de generación de documentos...
                      </p>
                    )}
                    <div className="grid grid-cols-2 gap-3">
                      <button
                        onClick={() => generatePDF()}
                        disabled={!librariesLoaded}
                        className={`flex items-center justify-center gap-2 p-3 rounded-lg font-semibold transition-all shadow-md ${
                          librariesLoaded 
                            ? 'bg-red-600 text-white hover:bg-red-700 hover:shadow-lg cursor-pointer' 
                            : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                        }`}
                      >
                        <span>📄</span>
                        Descargar PDF (Paciente)
                      </button>
                      <button
                        onClick={() => generateWordDoc()}
                        disabled={!librariesLoaded}
                        className={`flex items-center justify-center gap-2 p-3 rounded-lg font-semibold transition-all shadow-md ${
                          librariesLoaded 
                            ? 'bg-blue-600 text-white hover:bg-blue-700 hover:shadow-lg cursor-pointer' 
                            : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                        }`}
                      >
                        <span>📝</span>
                        Descargar Word (Editable)
                      </button>
                    </div>
                  </div>
                </div>
              </AlertDescription>
            </Alert>

            <Alert className="bg-red-50 border-2 border-red-400">
              <AlertDescription>
                <div className="flex items-start gap-3">
                  <AlertTriangle className="text-red-600 flex-shrink-0 mt-1" size={24} />
                  <div>
                    <h4 className="font-bold text-red-800 mb-3 text-lg">
                      ⚠️ Recordatorios Importantes Durante Todo el Tratamiento
                    </h4>
                    <div className="space-y-2 text-sm">
                      <div className="bg-white p-3 rounded border-l-4 border-red-500">
                        <strong className="text-red-800">🛡️ Protección gástrica:</strong>
                        <p className="mt-1">Omeprazol 20-40 mg/día en ayunas durante TODO el tratamiento</p>
                      </div>
                      
                      <div className="bg-white p-3 rounded border-l-4 border-blue-500">
                        <strong className="text-blue-800">🦠 Profilaxis Pneumocystis:</strong>
                        <p className="mt-1">Septrim Forte 1 comp: <strong>Lunes - Miércoles - Viernes</strong></p>
                        <p className="text-xs text-gray-600 mt-1">
                          (Obligatorio si prednisona ≥20 mg/día durante >4 semanas)
                        </p>
                      </div>
                      
                      <div className="bg-white p-3 rounded border-l-4 border-green-500">
                        <strong className="text-green-800">🦴 Protección ósea:</strong>
                        <p className="mt-1">Calcio 1200 mg/día + Vitamina D 800-2000 UI/día</p>
                      </div>
                      
                      <div className="bg-white p-3 rounded border-l-4 border-orange-500">
                        <strong className="text-orange-800">📊 Control glucemia:</strong>
                        <p className="mt-1">Vigilar aparición de diabetes esteroidea (especialmente con dosis altas)</p>
                      </div>
                      
                      <div className="bg-white p-3 rounded border-l-4 border-purple-500">
                        <strong className="text-purple-800">❌ NUNCA suspender bruscamente:</strong>
                        <p className="mt-1">Riesgo de insuficiencia suprarrenal aguda. Seguir pauta de descenso progresivo</p>
                      </div>

                      <div className="bg-yellow-100 p-3 rounded border-l-4 border-yellow-600 mt-3">
                        <strong className="text-yellow-900">⚠️ Consultar URGENTE si aparece:</strong>
                        <ul className="mt-2 ml-4 list-disc space-y-1">
                          <li>Fiebre >38°C</li>
                          <li>Disnea o dolor torácico</li>
                          <li>Síntomas neurológicos nuevos</li>
                          <li>Dolor abdominal intenso</li>
                          <li>Debilidad extrema o mareo</li>
                        </ul>
                      </div>
                    </div>
                  </div>
                </div>
              </AlertDescription>
            </Alert>
          </div>
        )}
      </div>
    </div>
  );

  if (!mode) {
    return (
      <div className="max-w-6xl mx-auto p-6">
        <Card className="border-3 border-blue-500 shadow-xl">
          <CardHeader className="bg-gradient-to-r from-blue-600 via-purple-600 to-blue-600 text-white">
            <CardTitle className="text-3xl text-center py-4">
              🏥 Sistema de Manejo de Toxicidad Inmunomediada
            </CardTitle>
            <p className="text-center text-blue-100 mt-2">
              Asistente clínico elaborado por el Dr. Joaquín Gimeno
            </p>
            <p className="text-center text-blue-100 text-sm">
              Basado en guías ESMO 2022 y NCCN 2026
            </p>
          </CardHeader>
          <CardContent className="p-8">
            <p className="mb-8 text-gray-700 text-lg text-center">
              Herramienta para el manejo de toxicidades por inmunoterapia y cálculo de pautas de descenso de corticoides
            </p>
            
            <div className="grid md:grid-cols-2 gap-6">
              <button
                onClick={() => setMode('toxicity')}
                className="group p-8 bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-xl hover:from-blue-600 hover:to-blue-700 transition-all shadow-lg hover:shadow-xl transform hover:-translate-y-1"
              >
                <div className="text-5xl mb-4">📋</div>
                <div className="text-2xl font-bold mb-3">Opción 1</div>
                <div className="text-xl mb-3">Recomendaciones por Toxicidad</div>
                <div className="text-sm opacity-90 leading-relaxed">
                  Obtén protocolos específicos según órgano afectado, tipo de toxicidad y grado de severidad.
                  Incluye manejo con corticoides, monitorización y decisión sobre inmunoterapia.
                </div>
              </button>
              
              <button
                onClick={() => setMode('calculator')}
                className="group p-8 bg-gradient-to-br from-purple-500 to-purple-600 text-white rounded-xl hover:from-purple-600 hover:to-purple-700 transition-all shadow-lg hover:shadow-xl transform hover:-translate-y-1"
              >
                <div className="text-5xl mb-4">🧮</div>
                <div className="text-2xl font-bold mb-3">Opción 2</div>
                <div className="text-xl mb-3">Calculadora de Descenso</div>
                <div className="text-sm opacity-90 leading-relaxed">
                  Calcula pautas personalizadas de descenso de corticoides con calendario semanal detallado.
                  Incluye conversión automática entre diferentes corticoides.
                </div>
              </button>
            </div>

            <div className="mt-8 p-4 bg-blue-50 rounded-lg border-2 border-blue-200">
              <div className="flex items-start gap-3">
                <Info className="text-blue-600 flex-shrink-0 mt-1" size={24} />
                <div className="text-sm text-gray-700">
                  <strong className="text-blue-900">Información importante:</strong>
                  <p className="mt-1">
                    Esta herramienta está basada en las guías ESMO 2022 para el manejo de toxicidades por inmunoterapia.
                    Las recomendaciones deben adaptarse al contexto clínico individual de cada paciente.
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6">
      <button
        onClick={() => {
          setMode(null);
          setSelectedOrgan('');
          setSelectedToxicity('');
          setSelectedGrade('');
          setShowCorticoidRecommendation(false);
          setShowAdditionalInfo(false);
          setTaperSchedule(null);
        }}
        className="mb-6 px-6 py-3 bg-gradient-to-r from-gray-600 to-gray-700 text-white rounded-lg hover:from-gray-700 hover:to-gray-800 font-semibold shadow-md hover:shadow-lg transition-all flex items-center gap-2"
      >
        <span>←</span> Volver al Menú Principal
      </button>
      
      <Card className="border-2 shadow-xl">
        <CardContent className="p-8">
          {mode === 'toxicity' && renderToxicityRecommendations()}
          {mode === 'calculator' && renderDoseCalculator()}
        </CardContent>
      </Card>
    </div>
  );
};

export default ToxicityManagementSystem;
