#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
# Copyright Kitware Inc. and Contributors
# Distributed under the Apache License, 2.0 (apache.org/licenses/LICENSE-2.0)
# See accompanying Copyright.txt and LICENSE files for details
###############################################################################

import itertools

from girder_worker.docker.tasks import docker_run
from girder_worker.docker.transforms import VolumePath
from girder_worker.docker.transforms.girder import (
    GirderFileIdToVolume,
    GirderUploadVolumePathToFolder,
)

from .common import (
    addJobInfo,
    createDockerRunArguments,
    createGirderClient,
    createUploadMetadata,
)
from ..constants import DockerImage


def classifyMaterials(
    initWorkingSetName,
    stepName,
    requestInfo,
    jobId,
    outputFolder,
    imageFiles,
    metadataFiles,
    modelFile,
    outfilePrefix,
    cuda=None,
    batchSize=None,
    model=None,
):
    """
    Run a Girder Worker job to classify materials in an orthorectified image.

    Requirements:
    - Danesfield Docker image is available on host

    :param initWorkingSetName: The name of the top-level working set.
    :type initWorkingSetName: str
    :param stepName: The name of the step.
    :type stepName: str (DanesfieldStep)
    :param requestInfo: HTTP request and authorization info.
    :type requestInfo: RequestInfo
    :param jobId: Job ID.
    :type jobId: str
    :param outputFolder: Output folder document.
    :type outputFolder: dict
    :param imageFiles: List of orthorectified MSI image files.
    :type imageFiles: list[dict]
    :param metadataFiles: List of MSI-source NITF metadata files.
    :type metadataFiles: list[dict]
    :param modelFile: Model file document.
    :type modelFile: dict
    :param outfilePrefix: Prefix for output filename
    :type outfilePrefix: str
    :param cuda: Enable/disable CUDA; enabled by default.
    :type cuda: bool
    :param batchSize: Number of pixels classified at a time.
    :type batchSize: int
    :returns: Job document.
    """
    gc = createGirderClient(requestInfo)

    outputVolumePath = VolumePath(".")

    # Docker container arguments
    containerArgs = list(
        itertools.chain(
            [
                "python",
                "danesfield/tools/material_classifier.py",
                "--model_path",
                GirderFileIdToVolume(modelFile["_id"], gc=gc),
                "--output_dir",
                outputVolumePath,
                "--outfile_prefix",
                outfilePrefix,
                "--image_paths",
            ],
            [GirderFileIdToVolume(imageFile["_id"], gc=gc) for imageFile in imageFiles],
            ["--info_paths"],
            [
                GirderFileIdToVolume(metadataFile["_id"], gc=gc)
                for metadataFile in metadataFiles
            ],
        )
    )
    if cuda is None or cuda:
        containerArgs.append("--cuda")
    if batchSize is not None:
        containerArgs.extend(["--batch_size", str(batchSize)])

    # Result hooks
    # - Upload output files to output folder
    # - Provide upload metadata
    upload_kwargs = createUploadMetadata(jobId, stepName)
    resultHooks = [
        GirderUploadVolumePathToFolder(
            outputVolumePath, outputFolder["_id"], upload_kwargs=upload_kwargs, gc=gc
        )
    ]

    asyncResult = docker_run.delay(
        runtime="nvidia",
        **createDockerRunArguments(
            image=DockerImage.DANESFIELD,
            containerArgs=containerArgs,
            jobTitle="[%s] Classify materials" % initWorkingSetName,
            jobType=stepName,
            user=requestInfo.user,
            resultHooks=resultHooks,
        )
    )

    # Add info for job event listeners
    job = asyncResult.job
    job = addJobInfo(job, jobId=jobId, stepName=stepName)

    return job
