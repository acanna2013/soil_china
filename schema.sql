-- RELEVANT FILES: us_soil_db.csv (Soil_Rule_Class folder)
-- AND china_soil_us.csv (China_Soil folder)
CREATE OR REPLACE TABLE 
HELIOS_MDI_INT_DB.MACHINE_DATA_VIZ.SOIL_DATA (
    LATITUDE NUMBER(4, 2) NOT NULL,
    LONGITUDE NUMBER(5,2) NOT NULL,
    COUNTRY VARCHAR(2),
    SAND_PCT NUMBER(5,2),
    SILT_PCT NUMBER(5,2),
    CLAY_PCT NUMBER(5,2),
    PI_VAL NUMBER(4,2),
    CLASS VARCHAR(4)
);

CREATE OR REPLACE TABLE 
HELIOS_MDI_INT_DB.MACHINE_DATA_VIZ.REBUILDS_DATA (
    SN_PREFIX VARCHAR(3) NOT NULL,
    BS_MDL VARCHAR(30),
    PROD_FAM_DESC VARCHAR(19),
    MACHINE_TYPE VARCHAR(13), -- ENGINE/UNDERCARRIAGE
    COMPONENT VARCHAR(30),
    JOB VARCHAR(30),
    FIRST_INTERVAL NUMBER(5, 0),
    NEXT_INTERVAL NUMBER(5, 0)
);

-- LOAD DATA INTO SNOWFLAKE VIA SNOWPIPE
-- COPY INTO [table_name] FROM [location (of s3 bucket)]
COPY INTO HELIOS_MDI_INT_DB.MACHINE_DATA_VIZ.SOIL_DATA 
FROM @S3_BUCKET_LOCATION
file_format = (type = 'csv');

COPY INTO HELIOS_MDI_INT_DB.MACHINE_DATA_VIZ.REBUILDS_DATA 
FROM @S3_BUCKET_LOCATION
file_format = (type = 'csv')