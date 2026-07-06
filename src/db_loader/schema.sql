-- UOW-2: DbLoader - テーブル・インデックスの冪等セットアップ(BR-2, BR-3)
-- 各ブロックは専用の区切りコメントで1文ずつ分割され、schema_setup.pyが順番に実行する

-- STATEMENT --
IF NOT EXISTS (
    SELECT * FROM sys.objects
    WHERE object_id = OBJECT_ID(N'[dbo].[A1_ProcessingMachine_Utilization_Rate]') AND type = N'U'
)
CREATE TABLE [dbo].[A1_ProcessingMachine_Utilization_Rate] (
    [Product_Number] VARCHAR(50) NOT NULL,
    [Machine_Name] VARCHAR(50) NOT NULL,
    [Machine_Number] VARCHAR(50) NOT NULL,
    [Processing_Start_Time] DATETIME NOT NULL,
    [Processing_Completion_Time] DATETIME NOT NULL,
    [Sum_DateTime] INT NOT NULL,
    [Pass judgment] VARCHAR(50) NOT NULL
);

-- STATEMENT --
IF NOT EXISTS (
    SELECT * FROM sys.indexes
    WHERE name = 'IX_A1_ProductNumber_MachineNumber'
      AND object_id = OBJECT_ID(N'[dbo].[A1_ProcessingMachine_Utilization_Rate]')
)
CREATE UNIQUE INDEX IX_A1_ProductNumber_MachineNumber
ON [dbo].[A1_ProcessingMachine_Utilization_Rate] ([Product_Number], [Machine_Number]);

-- STATEMENT --
IF NOT EXISTS (
    SELECT * FROM sys.indexes
    WHERE name = 'IX_A1_MachineName_StartTime'
      AND object_id = OBJECT_ID(N'[dbo].[A1_ProcessingMachine_Utilization_Rate]')
)
CREATE INDEX IX_A1_MachineName_StartTime
ON [dbo].[A1_ProcessingMachine_Utilization_Rate] ([Machine_Name], [Processing_Start_Time]);
