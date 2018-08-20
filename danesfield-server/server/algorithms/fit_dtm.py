#!/usr/bin/env python
# -*- coding: utf-8 -*-

##############################################################################
#  Copyright Kitware Inc.
#
#  Licensed under the Apache License, Version 2.0 ( the "License" );
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
##############################################################################

from girder_worker.docker.tasks import docker_run
from girder_worker.docker.transforms import VolumePath
from girder_worker.docker.transforms.girder import (
    GirderFileIdToVolume, GirderUploadVolumePathToFolder)

from .common import addJobInfo, createGirderClient, createUploadMetadata
from ..constants import DockerImage


def fitDtm(stepName, requestInfo, jobId, outputFolder, file, outputPrefix,
           iterations=None, tension=None):
    """
    Run a Girder Worker job to fit a Digital Terrain Model (DTM) to a Digital Surface Model (DSM).

    Requirements:
    - core3d/danesfield Docker image is available on host

    :param stepName: The name of the step.
    :type stepName: str (DanesfieldStep)
    :param requestInfo: HTTP request and authorization info.
    :type requestInfo: RequestInfo
    :param jobId: Job ID.
    :type jobId: str
    :param outputFolder: Output folder document.
    :type outputFolder: dict
    :param file: DSM image file document.
    :type file: dict
    :param outputPrefix: The prefix of the output file name.
    :type outputPrefix: str
    :param iterations: The base number of iterations at the coarsest scale.
    :type iterations: int
    :param tension: Number of inner smoothing iterations.
    :type tension: int
    :returns: Job document.
    """
    gc = createGirderClient(requestInfo)

    # Set output file name based on input file name
    dtmName = outputPrefix + '_DTM.tif'
    outputVolumePath = VolumePath(dtmName)

    # Docker container arguments
    containerArgs = [
        'danesfield/tools/fit_dtm.py',
        GirderFileIdToVolume(file['_id'], gc=gc),
        outputVolumePath
    ]
    if iterations is not None:
        containerArgs.extend(['--num-iterations', str(iterations)])
    if tension is not None:
        containerArgs.extend(['--tension', str(tension)])

    # Result hooks
    # - Upload output files to output folder
    # - Provide upload metadata
    upload_kwargs = createUploadMetadata(jobId, stepName)
    resultHooks = [
        GirderUploadVolumePathToFolder(
            outputVolumePath,
            outputFolder['_id'],
            upload_kwargs=upload_kwargs,
            gc=gc)
    ]

    asyncResult = docker_run.delay(
        image=DockerImage.DANESFIELD,
        pull_image=False,
        container_args=containerArgs,
        girder_job_title='Fit DTM: %s' % file['name'],
        girder_job_type=stepName,
        girder_result_hooks=resultHooks,
        girder_user=requestInfo.user)

    # Add info for job event listeners
    job = asyncResult.job
    job = addJobInfo(job, jobId=jobId, stepName=stepName)

    return job