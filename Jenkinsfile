// Release Multibranch: somente main, pasta release com credenciais Azure.
// CI de branches/PRs: Jenkinsfile.ci, pasta ci sem credenciais de deploy.
def azureSession(Closure action) {
  withCredentials([
    usernamePassword(credentialsId: 'azure-sp', usernameVariable: 'AZURE_CLIENT_ID', passwordVariable: 'AZURE_CLIENT_SECRET'),
    string(credentialsId: 'azure-tenant', variable: 'AZURE_TENANT_ID'),
    string(credentialsId: 'azure-subscription', variable: 'AZURE_SUBSCRIPTION_ID')
  ]) {
    withEnv(["AZURE_CONFIG_DIR=${pwd(tmp: true)}/azure-${env.BUILD_NUMBER}",
             "DOCKER_CONFIG=${pwd(tmp: true)}/docker-${env.BUILD_NUMBER}"]) {
      try { sh 'bash ci/azure-login.sh'; action() }
      finally {
        sh '''#!/usr/bin/env bash
          set +x
          az logout --output none >/dev/null 2>&1 || true
          rm -rf "$AZURE_CONFIG_DIR" "$DOCKER_CONFIG"
        '''
      }
    }
  }
}
pipeline {
  agent none
  options {
    skipDefaultCheckout(true)
    disableConcurrentBuilds()
    timestamps()
    timeout(time: 26, unit: 'HOURS')
    buildDiscarder(logRotator(numToKeepStr: '50', artifactNumToKeepStr: '50'))
  }
  parameters {
    string(name: 'AZURE_RG', defaultValue: 'rg-carparts-cicd', description: 'Grupo previamente provisionado')
    string(name: 'ACR_NAME', defaultValue: '', description: 'Nome globalmente único do ACR')
    string(name: 'HOM_APP', defaultValue: 'carparts-hom', description: 'Container App de homologação')
    string(name: 'PROD_APP', defaultValue: 'carparts-prod', description: 'Produção acadêmica')
  }
  environment {
    AZURE_RG = "${params.AZURE_RG}"
    ACR_NAME = "${params.ACR_NAME}"
    HOM_APP = "${params.HOM_APP}"
    PROD_APP = "${params.PROD_APP}"
  }
  stages {
    stage('Checkout e rastreabilidade') {
      agent { label 'linux && ci' }
      steps {
        deleteDir()
        checkout scm
        script {
          env.RELEASE_COMMIT = sh(script: 'git rev-parse HEAD', returnStdout: true).trim()
          env.COMMIT_EPOCH = sh(script: 'git show -s --format=%ct HEAD', returnStdout: true).trim()
          env.DEPLOY_ATTEMPTED = 'false'; env.DEPLOY_SUCCEEDED = 'false'
          env.DEPLOY_FAILED = 'false'
        }
        stash name: 'source', includes: '**', excludes: '.git/**,secrets/**,.env*'
      }
    }
    stage('Qualidade em paralelo') {
      parallel {
        stage('Sintaxe e segredos') {
          agent { label 'linux && ci' }
          steps {
            deleteDir(); unstash 'source'
            sh 'cd app && npm ci --ignore-scripts --no-audit --no-fund && npm run lint'
            sh 'python3 ci/audit.py'
          }
        }
        stage('Testes da API e front-end') {
          agent { label 'linux && ci' }
          steps {
            deleteDir(); unstash 'source'
            sh 'cd app && npm ci --ignore-scripts --no-audit --no-fund && npm test'
            sh 'node --test ci/test/*.test.mjs'
            sh 'python3 ci/test/metrics_test.py'
          }
          post { always { junit testResults: 'test-results.xml', allowEmptyResults: false } }
        }
      }
    }
    stage('Construir imagem uma única vez') {
      when { beforeAgent true; branch 'main' }
      agent { label 'linux && docker && release' }
      steps {
        deleteDir(); unstash 'source'
        sh '''#!/usr/bin/env bash
          set -euo pipefail
          [[ "$ACR_NAME" =~ ^[a-z0-9]{5,50}$ ]]
          docker build --build-arg GIT_COMMIT="$RELEASE_COMMIT" \
            -t "$ACR_NAME.azurecr.io/carparts:$RELEASE_COMMIT-$BUILD_NUMBER" .
        '''
      }
    }
    stage('Publicar no ACR e fixar digest') {
      when { beforeAgent true; branch 'main' }
      agent { label 'linux && docker && azure && release' }
      steps {
        deleteDir(); unstash 'source'
        script {
          azureSession {
            sh '''#!/usr/bin/env bash
              set -euo pipefail
              set +x
              az acr login --name "$ACR_NAME" --output none --only-show-errors
              docker push "$ACR_NAME.azurecr.io/carparts:$RELEASE_COMMIT-$BUILD_NUMBER"
              digest=$(az acr repository show --name "$ACR_NAME" \
                --image "carparts:$RELEASE_COMMIT-$BUILD_NUMBER" --query digest -o tsv --only-show-errors)
              [[ "$digest" =~ ^sha256:[a-f0-9]{64}$ ]]
              printf '%s/carparts@%s' "$ACR_NAME.azurecr.io" "$digest" > image-ref.txt
            '''
          }
          env.IMAGE_REF = readFile('image-ref.txt').trim()
        }
        archiveArtifacts artifacts: 'image-ref.txt', fingerprint: true
        stash name: 'image-ref', includes: 'image-ref.txt'
      }
    }
    stage('Homologação e smoke test') {
      when { beforeAgent true; branch 'main' }
      agent { label 'linux && azure && release' }
      steps {
        deleteDir(); unstash 'source'; unstash 'image-ref'
        timeout(time: 15, unit: 'MINUTES') {
          script { azureSession { sh 'bash ci/deploy.sh hom "$(cat image-ref.txt)"' } }
        }
      }
    }
    stage('Aprovação registrada') {
      when { branch 'main' }
      // agent none: espera sem ocupar executor.
      steps {
        timeout(time: 24, unit: 'HOURS') {
          script {
            env.APPROVED_BY = input(message: "Promover ${env.RELEASE_COMMIT} / ${env.IMAGE_REF}? Recuperação para a imagem anterior em caso de falha está incluída.",
              ok: 'Aprovar produção', submitter: 'release-manager', submitterParameter: 'APPROVER')
            env.APPROVED_AT = java.time.Instant.now().toString()
          }
        }
      }
    }
    stage('Arquivar autorização') {
      when { beforeAgent true; branch 'main' }
      agent { label 'linux && azure && release' }
      steps {
        deleteDir(); unstash 'source'; unstash 'image-ref'
        script {
          writeFile file: 'approval.json', text: groovy.json.JsonOutput.toJson([
            approver: env.APPROVED_BY, approvedAt: env.APPROVED_AT,
            commit: env.RELEASE_COMMIT, image: env.IMAGE_REF, buildUrl: env.BUILD_URL])
        }
        sh 'node ci/verify-approval.mjs approval.json "$(cat image-ref.txt)" "$RELEASE_COMMIT"'
        archiveArtifacts artifacts: 'approval.json', fingerprint: true
        stash name: 'approval', includes: 'approval.json'
      }
    }
    stage('Produção: promover o mesmo digest') {
      when { beforeAgent true; branch 'main' }
      agent { label 'linux && azure && release' }
      steps {
        deleteDir(); unstash 'source'; unstash 'image-ref'; unstash 'approval'
        timeout(time: 15, unit: 'MINUTES') {
          script {
            env.DEPLOY_ATTEMPTED = 'true'
            try {
              azureSession { sh 'bash ci/deploy.sh prod "$(cat image-ref.txt)"' }
              env.DEPLOY_SUCCEEDED = 'true'
              env.DEPLOYED_AT = java.time.Instant.now().toString()
            } catch (Exception failure) {
              env.DEPLOY_FAILED = 'true'
              throw failure
            }
          }
        }
      }
    }
  }
  post {
    always {
      script {
        if (env.BRANCH_NAME == 'main' && env.RELEASE_COMMIT) {
          node('linux && release') {
            deleteDir()
            def result = [schema: 1, buildNumber: env.BUILD_NUMBER, buildUrl: env.BUILD_URL,
              commit: env.RELEASE_COMMIT, commitEpoch: env.COMMIT_EPOCH,
              recordedAt: java.time.Instant.now().toString(), result: currentBuild.currentResult,
              productionAttempted: env.DEPLOY_ATTEMPTED == 'true',
              productionSucceeded: env.DEPLOY_SUCCEEDED == 'true',
              productionFailed: env.DEPLOY_FAILED == 'true',
              deployedAt: env.DEPLOYED_AT ?: null, image: env.IMAGE_REF ?: null,
              approver: env.APPROVED_BY ?: null, approvedAt: env.APPROVED_AT ?: null]
            writeFile file: 'run.json', text: groovy.json.JsonOutput.toJson(result)
            archiveArtifacts artifacts: 'run.json', fingerprint: true
            deleteDir()
          }
        }
      }
    }
    success { echo 'Pipeline concluída. Consulte testes, aprovação, digest e métricas nos artefatos.' }
    failure { echo 'Falha: promoção bloqueada ou recuperação acionada. Consulte o stage que falhou.' }
    aborted { echo 'Execução abortada: não produzir aprovação ou implantação fictícia.' }
  }
}
