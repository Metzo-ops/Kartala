DROP DATABASE IF EXISTS kartala;
-- Création de la base de données
CREATE DATABASE kartala;

USE kartala;

-- Création de la table Poles
CREATE TABLE Poles (
    IdPole INT AUTO_INCREMENT PRIMARY KEY,
    NomPole VARCHAR(100) NOT NULL
);

-- Création de la table Employes
CREATE TABLE Employes (
    IdEmploye INT AUTO_INCREMENT PRIMARY KEY,
    NomEmploye VARCHAR(50) NOT NULL,
    PrenomEmploye VARCHAR(50) NOT NULL,
    DateEmbauche DATE NOT NULL,
    DateFinContrat DATE,
    Age INT NOT NULL,
    Sexe CHAR(1) NOT NULL,
    StatutMatrimonial VARCHAR(20),
    NiveauEducation VARCHAR(50)
);

-- Création de la table Projets
CREATE TABLE Projets (
    IdProjet INT AUTO_INCREMENT PRIMARY KEY,
    NomProjet VARCHAR(100) NOT NULL,
    NomCommanditaire VARCHAR(100) NOT NULL,
    DureeProjet INT NOT NULL, -- Durée en jours
    DateDebutProjet DATE NOT NULL,
    DateFinPrevueProjet DATE NOT NULL,
    BudgetProjet DECIMAL(15,2) NOT NULL,
    IdCoordinateur INT NOT NULL,
    IdPole INT NOT NULL,
    FOREIGN KEY (IdCoordinateur) REFERENCES Employes(IdEmploye),
    FOREIGN KEY (IdPole) REFERENCES Poles(IdPole)
);

-- Création de la table Activites
CREATE TABLE Activites (
    IdActivite INT AUTO_INCREMENT PRIMARY KEY,
    LibelleActivite VARCHAR(200) NOT NULL,
    DureeActivite INT NOT NULL, -- Durée en jours
    DateDebutActivite DATE NOT NULL,
    DateFinPrevueActivite DATE NOT NULL,
    BudgetActivite DECIMAL(15,2) NOT NULL,
    IdProjet INT NOT NULL,
    FOREIGN KEY (IdProjet) REFERENCES Projets(IdProjet)
);

-- Création de la table EmployesAffectes
CREATE TABLE EmployesAffectes (
    IdEmploye INT NOT NULL,
    IdActivite INT NOT NULL,
    DateDebutRealisation DATE,
    DateFinRealisation DATE,
    PRIMARY KEY (IdEmploye, IdActivite),
    FOREIGN KEY (IdEmploye) REFERENCES Employes(IdEmploye),
    FOREIGN KEY (IdActivite) REFERENCES Activites(IdActivite)
);

-- Création des index pour des requêtes rapides
CREATE INDEX idx_employesaffectes_datedebut ON EmployesAffectes (DateDebutRealisation);
CREATE INDEX idx_employesaffectes_datefin ON EmployesAffectes (DateFinRealisation);

