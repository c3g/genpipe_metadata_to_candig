#!/usr/bin/env python3

import argparse
import json
import os
from pathlib import Path


BASEDIR = Path(__file__).resolve().parent
TEMPLATE_FILE = os.path.join(BASEDIR, 'pipeline_metadata_template.json')
OUTPUT_FILE = os.path.join(BASEDIR, 'output.json')


def find_software_version(json_list, software_key):
    for obj in json_list:
        if obj["name"] == software_key:
            return obj["version"]

    return None


def generate_output(input_file: str):
    with open(TEMPLATE_FILE) as f:
        template_json = json.load(f)
        template = template_json["pipeline_metadata"][0]

    with open(input_file) as f:
        pipeline_json = json.load(f)

    template["VariantCalling"]["site"] = "Montréal"
    template["Sequencing"]["site"] = "Montréal"
    template["Alignment"]["site"] = "Montréal"
    template["ExpressionAnalysis"]["site"] = "Montréal"

    if "sample_name" in pipeline_json:
        template["VariantCalling"]["sampleId"] = pipeline_json["sample_name"]
        template["Sequencing"]["sampleId"] = pipeline_json["sample_name"]
        template["Alignment"]["sampleId"] = pipeline_json["sample_name"]
        template["ExpressionAnalysis"]["sampleId"] = pipeline_json["sample_name"]

    pipeline_data = pipeline_json["pipeline"]

    if "general_information" in pipeline_data:
        template["Alignment"]["reference"] = pipeline_data["general_information"]["assembly_used"]
        template["ExpressionAnalysis"]["reference"] = pipeline_data["general_information"]["assembly_used"]

    # GenomeAnalysisTK in genpipes, GATK in CanDIG
    gatk_version = find_software_version(pipeline_data["software"], "GenomeAnalysisTK")
    fastqc_version = find_software_version(pipeline_data["software"], "fastqc")
    bwa_version = find_software_version(pipeline_data["software"], "bwa")
    sambamba_version = find_software_version(pipeline_data["software"], "sambamba")
    picard_version = find_software_version(pipeline_data["software"], "picard")
    samtools_version = find_software_version(pipeline_data["software"], "samtools")

    if fastqc_version:
        template["Alignment"]["fastqc"] = f"fastqc/{fastqc_version}"

    if bwa_version:
        template["Alignment"]["alignmentTool"] = f"BWA-MEM/{bwa_version}"

    if sambamba_version:
        template["Alignment"]["mergeTool"] = f"Sambamba/{sambamba_version}"

    if picard_version:
        template["Alignment"]["insertSizeMetrics"] = f"picard/{picard_version}"
        template["Alignment"]["markDuplicates"] = f"picard/{picard_version}"

    with open(OUTPUT_FILE, "w", encoding='utf8') as f:
        template_json["pipeline_metadata"][0] = template
        json.dump(template_json, f, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(
        description="Takes a JSON metadata file from genpipes and transforms it into CanDIG format"
    )
    parser.add_argument("input", metavar="input")

    args = parser.parse_args()

    if os.path.exists(args.input) and os.path.isfile(args.input):
        generate_output(args.input)


if __name__ == "__main__":
    main()
