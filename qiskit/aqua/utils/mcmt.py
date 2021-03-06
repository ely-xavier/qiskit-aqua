# -*- coding: utf-8 -*-

# Copyright 2018 IBM.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =============================================================================
"""
Multiple-Control, Multiple-Target Gate.
"""
from qiskit import QuantumCircuit, QuantumRegister


def _ccx_v_chain_compute(qc, control_qubits, ancillary_qubits):
    """
    First half (compute) of the multi-control basic mode. It progressively compute the
    ccx of the control qubits and put the final result in the last ancillary
    qubit
    Args:
        qc: the QuantumCircuit
        control_qubits: the list of control qubits
        ancillary_qubits: the list of ancillary qubits

    """
    anci_idx = 0
    qc.ccx(control_qubits[0], control_qubits[1], ancillary_qubits[anci_idx])
    for idx in range(2, len(control_qubits)):
        assert anci_idx + 1 < len(
            ancillary_qubits
        ), "Insufficient number of ancillary qubits {0}.".format(
            len(ancillary_qubits))
        qc.ccx(control_qubits[idx], ancillary_qubits[anci_idx],
               ancillary_qubits[anci_idx + 1])
        anci_idx += 1


def _ccx_v_chain_uncompute(qc, control_qubits, ancillary_qubits):
    """
    Second half (uncompute) of the multi-control basic mode. It progressively compute the
    ccx of the control qubits and put the final result in the last ancillary
    qubit
    Args:
        qc: the QuantumCircuit
        control_qubits: the list of control qubits
        ancillary_qubits: the list of ancillary qubits

    """
    anci_idx = len(ancillary_qubits) - 1
    for idx in (range(2, len(control_qubits)))[::-1]:
        qc.ccx(control_qubits[idx], ancillary_qubits[anci_idx - 1],
               ancillary_qubits[anci_idx])
        anci_idx -= 1
    qc.ccx(control_qubits[0], control_qubits[1], ancillary_qubits[anci_idx])


def mcmt(self,
         q_controls,
         q_ancillae,
         single_control_gate_fun,
         q_targets,
         mode="basic"):
    """
    Apply a Multi-Control, Multi-Target using a generic gate.
    It can also be used to implement a generic Multi-Control gate, as the target could also be of length 1.
    Args:

        q_controls: The list of control qubits
        q_ancillae: The list of ancillary qubits
        single_control_gate_fun: The single control gate function (e.g QuantumCircuit.cz or QuantumCircuit.ch)
        q_targets: A list of qubits or a QuantumRegister to which the gate function should be applied.
        mode (string): The implementation mode to use (at the moment, only the basic mode is supported)

    """
    # check controls
    if isinstance(q_controls, QuantumRegister):
        control_qubits = [qb for qb in q_controls]
    elif isinstance(q_controls, list):
        control_qubits = q_controls
    else:
        raise ValueError(
            'MCT needs a list of qubits or a quantum register for controls.')

    # check target
    if isinstance(q_targets, QuantumRegister):
        target_qubits = [qb for qb in q_targets]
    elif isinstance(q_targets, list):
        target_qubits = q_targets
    else:
        raise ValueError(
            'MCT needs a list of qubits or a quantum register for targets.')

    # check ancilla
    if q_ancillae is None:
        ancillary_qubits = []
    elif isinstance(q_ancillae, QuantumRegister):
        ancillary_qubits = [qb for qb in q_ancillae]
    elif isinstance(q_ancillae, list):
        ancillary_qubits = q_ancillae
    else:
        raise ValueError(
            'MCT needs None or a list of qubits or a quantum register for ancilla.'
        )

    all_qubits = control_qubits + target_qubits + ancillary_qubits
    for qubit in all_qubits:
        self._check_qubit(qubit)
    self._check_dups(all_qubits)

    if len(q_controls) == 1:
        for qubit in target_qubits:
            single_control_gate_fun(self, q_controls[0], qubit)
        return

    if mode == 'basic':
        # last ancillary qubit is the control of the gate
        ancn = len(ancillary_qubits)
        _ccx_v_chain_compute(self, control_qubits, ancillary_qubits)
        for qubit in target_qubits:
            single_control_gate_fun(self, ancillary_qubits[ancn - 1], qubit)
        _ccx_v_chain_uncompute(self, control_qubits, ancillary_qubits)
    else:
        raise ValueError(
            'Unrecognized mode "{0}" for building mcmt circuit, at the moment only "basic" mode is supported.'
            .format(mode))


QuantumCircuit.mcmt = mcmt
