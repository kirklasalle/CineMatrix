"""Pytest fixtures shared across all test modules."""
import sys
import os
import pytest

# Ensure both project root and backend are on the path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
project_root = os.path.dirname(backend_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)



@pytest.fixture
def sample_screenplay_text():
    return """FADE IN:

INT. POLICE STATION — INTERROGATION ROOM — NIGHT

DETECTIVE COLE (40s, weathered) sits across from a SUSPECT.

DETECTIVE COLE
Where were you on the night of the fourteenth?

SUSPECT
(nervous)
I was home. Alone.

DETECTIVE COLE
Nobody saw you.

EXT. ALLEY BEHIND STATION — NIGHT

Cole lights a cigarette. Stares at the wall. Thinking.

INT. POLICE STATION — DETECTIVE'S OFFICE — LATER

Cole pins photographs to a board. A pattern emerges.
"""


@pytest.fixture
def sample_fountain_text():
    return """Title: Test Film
Author: Test Author
Draft date: 2026-07-03

FADE IN:

INT. COFFEE SHOP - MORNING

SARAH (30s) reads a newspaper. Frowns.

SARAH
This can't be right.

She pulls out her phone.

EXT. CITY STREET - DAY

Sarah walks fast. Eyes forward.

FADE TO BLACK.
"""


@pytest.fixture
def sample_fdx_text():
    return """<?xml version="1.0" encoding="UTF-8"?>
<FinalDraft DocumentType="Script" Version="4">
  <Content>
    <Paragraph Type="Scene Heading">
      <Text>INT. OFFICE - DAY</Text>
    </Paragraph>
    <Paragraph Type="Action">
      <Text>JOHN sits at his desk, reviewing papers.</Text>
    </Paragraph>
    <Paragraph Type="Character">
      <Text>JOHN</Text>
    </Paragraph>
    <Paragraph Type="Dialogue">
      <Text>This changes everything.</Text>
    </Paragraph>
    <Paragraph Type="Scene Heading">
      <Text>EXT. PARKING LOT - NIGHT</Text>
    </Paragraph>
    <Paragraph Type="Action">
      <Text>John walks to his car. Checks over his shoulder.</Text>
    </Paragraph>
  </Content>
</FinalDraft>
"""


@pytest.fixture
def sample_stage_play_text():
    return """THE TEST PLAY
A Drama in Two Acts

ACT ONE

SCENE 1

[A bare stage. A table. Two chairs. ALICE and BOB sit across from each other.]

ALICE: You knew all along.

BOB: (carefully) I knew enough.

ALICE: That's not an answer.

ACT TWO

SCENE 1

[The same room. Hours later. The chairs have moved.]

BOB: She came back.

ALICE: I know. I let her in.
"""
